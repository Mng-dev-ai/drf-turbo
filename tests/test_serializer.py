import pickle
import re
from collections import ChainMap
from collections.abc import Mapping

import pytest

import drf_turbo as dt
from drf_turbo.exceptions import OnlyAndExcludeError


class TestSerializer:
    def setup(self):
        class ExampleSerializer(dt.Serializer):
            char = dt.StrField()
            integer = dt.IntField()

        self.Serializer = ExampleSerializer
        self.context = {}

    def test_valid_serializer(self):
        serializer = self.Serializer(data={"char": "abc", "integer": 123})
        assert serializer.is_valid()
        assert serializer.validated_data == {"char": "abc", "integer": 123}
        assert serializer.data == {"char": "abc", "integer": 123}
        assert serializer.errors == {}

    def test_invalid_serializer(self):
        serializer = self.Serializer(data={"char": "abc"})
        assert not serializer.is_valid()
        assert serializer.validated_data == {}
        assert serializer.data == {"char": "abc"}
        assert serializer.errors == {"integer": ["This field is required."]}

    def test_invalid_datatype(self):
        serializer = self.Serializer(data=[{"char": "abc"}])
        assert not serializer.is_valid()
        assert serializer.validated_data == {}
        # assert serializer.data == {}
        assert serializer.errors == ["Invalid data type: list"]

    def test_partial_validation(self):
        serializer = self.Serializer(data={"char": "abc"}, partial=True)
        assert serializer.is_valid()
        assert serializer.validated_data == {"char": "abc"}
        assert serializer.errors == {}

    def test_empty_serializer(self):
        serializer = self.Serializer()
        assert serializer.data == {"char": "", "integer": None}

    def test_missing_attribute_during_serialization(self):
        class MissingAttributes:
            pass

        instance = MissingAttributes()
        serializer = self.Serializer(instance)
        with pytest.raises(AttributeError):
            serializer.data

    def test_data_access_before_save_raises_error(self):
        def create(validated_data):
            return validated_data

        serializer = self.Serializer(data={"char": "abc", "integer": 123})
        serializer.create = create
        assert serializer.is_valid()
        assert serializer.data == {"char": "abc", "integer": 123}
        with pytest.raises(AssertionError):
            serializer.save()

    def test_validate_none_data(self):
        data = None
        serializer = self.Serializer(data=data)
        assert not serializer.is_valid()
        assert serializer.errors == ["Invalid data type: NoneType"]

    def test_serialize_chainmap(self):
        data = ChainMap({"char": "abc"}, {"integer": 123})
        serializer = self.Serializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data == {"char": "abc", "integer": 123}
        assert serializer.errors == {}

    def test_serialize_custom_mapping(self):
        class SinglePurposeMapping(Mapping):
            def __getitem__(self, key):
                return "abc" if key == "char" else 123

            def __iter__(self):
                yield "char"
                yield "integer"

            def __len__(self):
                return 2

        serializer = self.Serializer(data=SinglePurposeMapping())
        assert serializer.is_valid()
        assert serializer.validated_data == {"char": "abc", "integer": 123}
        assert serializer.errors == {}

    def test_custom_deserialize(self):
        """
        deserialize() is expected to return a dict, but subclasses may
        return application specific type.
        """

        class Point:
            def __init__(self, srid, x, y):
                self.srid = srid
                self.coords = (x, y)

        # Declares a serializer that converts data into an object
        class NestedPointSerializer(dt.Serializer):
            longitude = dt.FloatField(attr="x")
            latitude = dt.FloatField(attr="y")

            def deserialize(self, data, context):
                kwargs = super().deserialize(data, context)
                return Point(srid=4326, **kwargs)

        serializer = NestedPointSerializer(
            data={"longitude": 6.958307, "latitude": 50.941357}
        )
        assert serializer.is_valid()
        assert isinstance(serializer.validated_data, Point)
        assert serializer.validated_data.srid == 4326
        assert serializer.validated_data.coords[0] == 6.958307
        assert serializer.validated_data.coords[1] == 50.941357
        assert serializer.errors == {}

    def test_iterable_validators(self):
        """
        Ensure `validators` parameter is compatible with reasonable iterables.
        """
        data = {"char": "abc", "integer": 123}

        for validators in ([], (), set()):

            class ExampleSerializer(dt.Serializer):
                char = dt.StrField(validators=validators)
                integer = dt.IntField()

            serializer = ExampleSerializer(data=data)
            assert serializer.is_valid()
            assert serializer.validated_data == data
            assert serializer.errors == {}

        def raise_exception(value):
            raise dt.ValidationError("Raised error")

        for validators in ([raise_exception], (raise_exception,), {raise_exception}):

            class ExampleSerializer(dt.Serializer):
                char = dt.StrField(validators=validators)
                integer = dt.IntField()

            serializer = ExampleSerializer(data=data)
            assert not serializer.is_valid()
            assert serializer.data == data
            assert serializer.validated_data == {}

    def test_only_fields(self):
        class ExampleSerializer(dt.Serializer):
            char = dt.StrField()
            integer = dt.IntField()

        serializer = ExampleSerializer({"char": "abc", "integer": 123}, only=("char",))
        assert serializer.data == {"char": "abc"}

    def test_exclude_fields(self):
        class ExampleSerializer(dt.Serializer):
            char = dt.StrField()
            integer = dt.IntField()

        serializer = ExampleSerializer(
            {"char": "abc", "integer": 123}, exclude=("char",)
        )
        assert serializer.data == {"integer": 123}

    def test_not_allowed_only_and_exclude_fields(self):
        class ExampleSerializer(dt.Serializer):
            char = dt.StrField()
            integer = dt.IntField()

        with pytest.raises(OnlyAndExcludeError):

            ExampleSerializer(
                {"char": "abc", "integer": 123}, only=("char",), exclude=("integer",)
            )

    def test_nested_only_fields(self):
        class ExampleSerializer(dt.Serializer):
            char = dt.StrField()
            integer = dt.IntField()

        class NestedSerializer(dt.Serializer):
            example = ExampleSerializer()

        serializer = NestedSerializer(
            {"example": {"char": "abc", "integer": 123}}, only=("example__char",)
        )
        assert serializer.data == {"example": {"char": "abc"}}

    def test_nested_exclude_fields(self):
        class ExampleSerializer(dt.Serializer):
            char = dt.StrField()
            integer = dt.IntField()

        class NestedSerializer(dt.Serializer):
            example = ExampleSerializer()

        serializer = NestedSerializer(
            {"example": {"char": "abc", "integer": 123}}, exclude=("example__char",)
        )
        assert serializer.data == {"example": {"integer": 123}}

    def test_nested_only_inheritance(self):
        class ExampleSerializer(dt.Serializer):
            char = dt.StrField()
            integer = dt.IntField()
            other = dt.StrField()

        class NestedSerializer(dt.Serializer):
            foo = dt.StrField()
            bar = dt.IntField()
            example = ExampleSerializer(only=("char", "other"))

        serializer = NestedSerializer(
            {
                "foo": "foo",
                "bar": 123,
                "example": {"char": "abc", "integer": 123, "other": "other"},
            },
            only=("foo", "example__other"),
        )
        assert serializer.data == {"example": {"other": "other"}, "foo": "foo"}

    def test_nested_exclude_inheritance(self):
        class ExampleSerializer(dt.Serializer):
            char = dt.StrField()
            integer = dt.IntField()
            other = dt.StrField()

        class NestedSerializer(dt.Serializer):
            foo = dt.StrField()
            bar = dt.IntField()
            example = ExampleSerializer(exclude=("char",))

        serializer = NestedSerializer(
            {
                "foo": "foo",
                "bar": 123,
                "example": {"char": "abc", "integer": 123, "other": "other"},
            },
            exclude=("foo", "example__other"),
        )
        assert serializer.data == {"example": {"integer": 123}, "bar": 123}


class TestValidateMethod:
    def test_non_field_error_validate_method(self):
        class ExampleSerializer(dt.Serializer):
            char = dt.StrField()
            integer = dt.IntField()

            def validate(self, attrs):
                raise dt.ValidationError("Non field error")

        serializer = ExampleSerializer(data={"char": "abc", "integer": 123})
        assert not serializer.is_valid()
        assert serializer.errors == ["Non field error"]

    def test_field_error_validate_method(self):
        class ExampleSerializer(dt.Serializer):
            char = dt.StrField()
            integer = dt.IntField()

            def validate(self, attrs):
                raise dt.ValidationError({"char": "Field error"})

        serializer = ExampleSerializer(data={"char": "abc", "integer": 123})
        assert not serializer.is_valid()
        assert serializer.errors == {"char": "Field error"}


class MockObject:
    def __init__(self, **kwargs):
        self._kwargs = kwargs
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __str__(self):
        kwargs_str = ", ".join(
            ["%s=%s" % (key, value) for key, value in sorted(self._kwargs.items())]
        )
        return "<MockObject %s>" % kwargs_str


class TestNotRequiredOutput:
    def test_not_required_output_for_dict(self):
        """
        'required=False' should allow a dictionary key to be missing in output.
        """

        class ExampleSerializer(dt.Serializer):
            omitted = dt.StrField(required=False)
            included = dt.StrField()

        serializer = ExampleSerializer(data={"included": "abc"})
        serializer.is_valid()
        assert serializer.data == {"included": "abc"}

    def test_not_required_output_for_object(self):
        """
        'required=False' should allow an object attribute to be missing in output.
        """

        class ExampleSerializer(dt.Serializer):
            omitted = dt.StrField(required=False)
            included = dt.StrField()

            def create(self, validated_data):
                return MockObject(**validated_data)

        serializer = ExampleSerializer(data={"included": "abc"})
        serializer.is_valid()
        serializer.save()
        assert serializer.data == {"included": "abc"}


class TestDefaultOutput:
    def setup(self):
        class ExampleSerializer(dt.Serializer):
            has_default = dt.StrField(default_value="x", required=False)
            has_default_callable = dt.StrField(
                default_value=lambda: "y", required=False
            )
            no_default = dt.StrField()

        self.Serializer = ExampleSerializer

    def test_default_used_for_dict(self):
        """
        'default="something"' should be used if dictionary key is missing from input.
        """
        serializer = self.Serializer({"no_default": "abc"})
        assert serializer.data == {
            "has_default": "x",
            "has_default_callable": "y",
            "no_default": "abc",
        }

    def test_default_used_for_object(self):
        """
        'default="something"' should be used if object attribute is missing from input.
        """
        instance = MockObject(no_default="abc")
        serializer = self.Serializer(instance)
        assert serializer.data == {
            "has_default": "x",
            "has_default_callable": "y",
            "no_default": "abc",
        }

    def test_default_not_used_when_in_dict(self):
        """
        'default="something"' should not be used if dictionary key is present in input.
        """
        serializer = self.Serializer(
            {"has_default": "def", "has_default_callable": "ghi", "no_default": "abc"}
        )
        assert serializer.data == {
            "has_default": "def",
            "has_default_callable": "ghi",
            "no_default": "abc",
        }

    def test_default_not_used_when_in_object(self):
        """
        'default="something"' should not be used if object attribute is present in input.
        """
        instance = MockObject(
            has_default="def", has_default_callable="ghi", no_default="abc"
        )
        serializer = self.Serializer(instance)
        assert serializer.data == {
            "has_default": "def",
            "has_default_callable": "ghi",
            "no_default": "abc",
        }

    def test_default_for_dotted_source(self):
        """
        'default="something"' should be used when a traversed attribute is missing from input.
        """

        class Serializer(dt.Serializer):
            traversed = dt.StrField(
                default_value="x", attr="traversed.attr", required=False
            )

        assert Serializer({}).data == {"traversed": "x"}
        assert Serializer({"traversed": {}}).data == {"traversed": "x"}
        assert Serializer({"traversed": None}).data == {"traversed": "x"}

        assert Serializer({"traversed": {"attr": "abc"}}).data == {"traversed": "abc"}

    def test_default_for_nested_serializer(self):
        class NestedSerializer(dt.Serializer):
            a = dt.StrField(default_value="1", required=False)
            c = dt.StrField(default_value="2", attr="b.c", required=False)

        class Serializer(dt.Serializer):
            nested = NestedSerializer()

        assert Serializer({"nested": None}).data == {"nested": None}
        assert Serializer({"nested": {}}).data == {"nested": {"a": "1", "c": "2"}}
        assert Serializer({"nested": {"a": "3", "b": {}}}).data == {
            "nested": {"a": "3", "c": "2"}
        }
        assert Serializer({"nested": {"a": "3", "b": {"c": "4"}}}).data == {
            "nested": {"a": "3", "c": "4"}
        }

    def test_default_for_allow_null(self):
        """
        Without an explicit default, allow_null implies default=None when serializing. #5518 #5708
        """

        class Serializer(dt.Serializer):
            foo = dt.StrField()
            bar = dt.StrField(attr="foo.bar", allow_null=True)
            optional = dt.StrField(required=False, allow_null=True)

        # allow_null=True should imply default=None when serializing:
        assert Serializer({"foo": None}).data == {
            "foo": None,
            "bar": None,
            "optional": None,
        }


class TestCacheSerializerData:
    def test_cache_serializer_data(self):
        """
        Caching serializer data with pickle will drop the serializer info,
        but does preserve the data itself.
        """

        class ExampleSerializer(dt.Serializer):
            field1 = dt.StrField()
            field2 = dt.StrField()

        serializer = ExampleSerializer({"field1": "a", "field2": "b"})
        pickled = pickle.dumps(serializer.data)
        data = pickle.loads(pickled)
        assert data == {"field1": "a", "field2": "b"}


class TestDefaultInclusions:
    def setup(self):
        class ExampleSerializer(dt.Serializer):
            char = dt.StrField(default_value="abc", required=False)
            integer = dt.IntField()

        self.Serializer = ExampleSerializer

    def test_default_should_included_on_create(self):
        serializer = self.Serializer(data={"integer": 456})
        assert serializer.is_valid()
        assert serializer.validated_data == {"char": "abc", "integer": 456}
        assert serializer.errors == {}

    def test_default_should_be_included_on_update(self):
        instance = MockObject(char="def", integer=123)
        serializer = self.Serializer(instance, data={"integer": 456})
        assert serializer.is_valid()
        assert serializer.validated_data == {"char": "abc", "integer": 456}
        assert serializer.errors == {}

    def test_default_should_not_be_included_on_partial_update(self):
        instance = MockObject(char="def", integer=123)
        serializer = self.Serializer(instance, data={"integer": 456}, partial=True)
        assert serializer.is_valid()
        assert serializer.validated_data == {"integer": 456}
        assert serializer.errors == {}


class TestSerializerValidationWithCompiledRegexField:
    def setup(self):
        class ExampleSerializer(dt.Serializer):
            name = dt.RegexField(re.compile(r"\d"), required=True)

        self.Serializer = ExampleSerializer

    def test_validation_success(self):
        serializer = self.Serializer(data={"name": "2"})
        assert serializer.is_valid()
        assert serializer.validated_data == {"name": "2"}
        assert serializer.errors == {}
