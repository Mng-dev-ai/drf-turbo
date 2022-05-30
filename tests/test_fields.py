import datetime
import uuid
from datetime import timezone
from decimal import Decimal

import pytest
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.test import APISimpleTestCase

import drf_turbo as dt
from drf_turbo.exceptions import ValidationError

NO_DEFAULT = object()


def get_items(mapping_or_list_of_two_tuples):
    # Tests accept either lists of two tuples, or dictionaries.
    if isinstance(mapping_or_list_of_two_tuples, dict):
        # {value: expected}
        return mapping_or_list_of_two_tuples.items()
    # [(value, expected), ...]
    return mapping_or_list_of_two_tuples


class FieldValues:
    """
    Base class for testing valid and invalid input values.
    """

    context = {}

    def test_valid_inputs(self):
        """
        Ensure that valid values return the expected validated data.
        """
        for input_value, expected_output in get_items(self.valid_inputs):
            assert (
                self.field.run_validation(input_value, self.context) == expected_output
            ), "input value: {}".format(repr(input_value))

    def test_invalid_inputs(self):
        """
        Ensure that invalid values raise the expected validation error.
        """
        for input_value, expected_failure in get_items(self.invalid_inputs):
            with pytest.raises(ValidationError) as exc_info:
                self.field.run_validation(input_value, self.context)
            assert exc_info.value.detail == expected_failure, "input value: {}".format(
                repr(input_value)
            )

    def test_outputs(self):
        for output_value, expected_output in get_items(self.outputs):
            assert (
                self.field.serialize(output_value, self.context) == expected_output
            ), "output value: {}".format(repr(output_value))


class TestStrField(FieldValues):
    """
    Valid and invalid values for `CharField`.
    """

    valid_inputs = {1: "1", "abc": "abc"}
    invalid_inputs = {
        (): ["Not a valid string."],
        True: ["Not a valid string."],
        "": ["May not be blank."],
    }
    outputs = {1: "1", "abc": "abc"}
    field = dt.StrField()

    def test_trim_whitespace_default(self):
        field = dt.StrField()
        assert field.deserialize(" abc ", self.context) == "abc"

    def test_trim_whitespace_disabled(self):
        field = dt.StrField(trim_whitespace=False)
        assert field.deserialize(" abc ", self.context) == " abc "

    def test_disallow_blank_with_trim_whitespace(self):
        field = dt.StrField(allow_blank=False, trim_whitespace=True)

        with pytest.raises(ValidationError) as exc_info:
            field.run_validation("   ", self.context)
        assert exc_info.value.detail == ["May not be blank."]

    def test_null_bytes(self):
        field = dt.StrField()

        for value in ("\0", "foo\0", "\0foo", "foo\0foo"):
            with pytest.raises(ValidationError) as exc_info:
                field.run_validation(value, self.context)
            assert exc_info.value.detail == ["Null characters are not allowed."]


class TestEmailField(FieldValues):
    """
    Valid and invalid values for `EmailField`.
    """

    valid_inputs = {
        "example@example.com": "example@example.com",
    }
    invalid_inputs = {"examplecom": ["Enter a valid email address."]}
    outputs = {}
    field = dt.EmailField()


class TestRegexField(FieldValues):
    """
    Valid and invalid values for `RegexField`.
    """

    valid_inputs = {
        "a9": "a9",
    }
    invalid_inputs = {"A9": ["This value does not match the required pattern."]}
    outputs = {}
    field = dt.RegexField(regex="[a-z][0-9]")


class TestURLField(FieldValues):
    """
    Valid and invalid values for `URLField`.
    """

    valid_inputs = {
        "http://example.com": "http://example.com",
    }
    invalid_inputs = {"example.com": ["Enter a valid URL."]}
    outputs = {}
    field = dt.URLField()


class TestUUIDField(FieldValues):
    """
    Valid and invalid values for `UUIDField`.
    """

    valid_inputs = {
        "825d7aeb-05a9-45b5-a5b7-05df87923cda": uuid.UUID(
            "825d7aeb-05a9-45b5-a5b7-05df87923cda"
        ),
    }
    invalid_inputs = {
        "825d7aeb-05a9-45b5-a5b7": ["Not a valid UUID."],
    }
    outputs = {
        uuid.UUID(
            "825d7aeb-05a9-45b5-a5b7-05df87923cda"
        ): "825d7aeb-05a9-45b5-a5b7-05df87923cda"
    }
    field = dt.UUIDField()


class TestSlugField(FieldValues):
    """
    Valid and invalid values for `SlugField`.
    """

    valid_inputs = {
        "slug-99": "slug-99",
    }
    invalid_inputs = {"slug 99": ["Not a valid slug."]}
    outputs = {}
    field = dt.SlugField()

    def test_allow_unicode_true(self):
        field = dt.SlugField(allow_unicode=True)

        validation_error = False
        try:
            field.run_validation("slug-99-\u0420", self.context)
        except dt.ValidationError:
            validation_error = True

        assert not validation_error


class TestIntField(FieldValues):
    """
    Valid and invalid values for `IntegerField`.
    """

    valid_inputs = {
        "1": 1,
        1: 1,
    }
    invalid_inputs = {
        0.5: ["A valid integer is required."],
        "abc": ["A valid integer is required."],
    }
    outputs = {
        "1": 1,
        "0": 0,
    }
    field = dt.IntField()


class TestMinMaxIntField(FieldValues):
    """
    Valid and invalid values for `IntegerField` with min and max limits.
    """

    valid_inputs = {
        "1": 1,
        3: 3,
    }
    invalid_inputs = {
        0: ["Must be greater than or equal to 1."],
        "4": ["Must be less than or equal to 3."],
    }
    outputs = {}
    field = dt.IntField(min_value=1, max_value=3)


class TestFloatField(FieldValues):
    """
    Valid and invalid values for `FloatField`.
    """

    valid_inputs = {
        "1": 1.0,
        "0": 0.0,
    }
    invalid_inputs = {"abc": ["A valid number is required."]}
    outputs = {
        "1": 1.0,
        "0": 0.0,
    }
    field = dt.FloatField()


class TestMinMaxFloatField(FieldValues):
    """
    Valid and invalid values for `FloatField` with min and max limits.
    """

    valid_inputs = {
        "1": 1,
        3: 3,
        1.0: 1.0,
    }
    invalid_inputs = {
        0.9: ["Must be greater than or equal to 1."],
        "3.1": ["Must be less than or equal to 3."],
    }
    outputs = {}
    field = dt.FloatField(min_value=1, max_value=3)


class TestDecimalField(FieldValues):
    """
    Valid and invalid values for `DecimalField`.
    """

    valid_inputs = {
        "12.3": Decimal("12.3"),
        "0.1": Decimal("0.1"),
        10: Decimal("10"),
    }
    invalid_inputs = (
        ("", ["A valid number is required."]),
        (" ", ["A valid number is required."]),
        ("abc", ["A valid number is required."]),
        (Decimal("Nan"), ["A valid number is required."]),
    )
    outputs = {
        "1": "1.0",
        "0": "0.0",
        1: "1.0",
        0: "0.0",
        Decimal("1.09"): "1.1",
        Decimal("0.04"): "0.0",
    }
    field = dt.DecimalField(max_digits=3, decimal_places=1)


class TestAllowNullDecimalField(FieldValues):
    valid_inputs = {
        "": None,
        " ": None,
    }
    invalid_inputs = {}
    outputs = {
        None: "",
    }
    field = dt.DecimalField(max_digits=3, decimal_places=1, allow_null=True)


class TestAllowNullNoStringCoercionDecimalField(FieldValues):
    valid_inputs = {
        "": None,
        " ": None,
    }
    invalid_inputs = {}
    outputs = {
        None: None,
    }
    field = dt.DecimalField(
        max_digits=3, decimal_places=1, allow_null=True, coerce_to_string=False
    )


class TestMinMaxDecimalField(FieldValues):
    """
    Valid and invalid values for `DecimalField` with min and max limits.
    """

    valid_inputs = {
        "10.0": Decimal("10.0"),
        "20.0": Decimal("20.0"),
    }
    invalid_inputs = {
        "9.9": ["Must be greater than or equal to 10."],
        "20.1": ["Must be less than or equal to 20."],
    }
    outputs = {}
    field = dt.DecimalField(max_digits=3, decimal_places=1, min_value=10, max_value=20)


class TestNoDecimalPlaces(FieldValues):
    valid_inputs = {
        "0.12345": Decimal("0.12345"),
    }
    invalid_inputs = {
        "0.1234567": ["Ensure that there are no more than 6 digits in total."]
    }
    outputs = {
        "1.2345": "1.2345",
        "0": "0",
        "1.1": "1.1",
    }
    field = dt.DecimalField(max_digits=6, decimal_places=None)


class TestNoMaxDigitsDecimalField(FieldValues):
    field = dt.DecimalField(
        max_value=100, min_value=0, decimal_places=2, max_digits=None
    )
    valid_inputs = {"10": Decimal("10.00")}
    invalid_inputs = {}
    outputs = {}


class TestDateField(FieldValues):
    """
    Valid and invalid values for `DateField`.
    """

    valid_inputs = {
        "2001-01-01": datetime.date(2001, 1, 1),
        datetime.date(2001, 1, 1): datetime.date(2001, 1, 1),
    }
    invalid_inputs = {
        "abc": ["Not a valid date."],
        "2001-99-99": ["Not a valid date."],
        "2001": ["Not a valid date."],
        datetime.datetime(2001, 1, 1, 12, 00): ["Expected a date but got a datetime."],
    }
    outputs = {
        datetime.date(2001, 1, 1): "2001-01-01",
        "2001-01-01": "2001-01-01",
        str("2016-01-10"): "2016-01-10",
        None: None,
        "": None,
    }
    field = dt.DateField()


class TestDateTimeField(FieldValues):
    """
    Valid and invalid values for `DateTimeField`.
    """

    valid_inputs = {
        "2001-01-01 13:00": datetime.datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc),
        "2001-01-01T13:00": datetime.datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc),
        "2001-01-01T13:00Z": datetime.datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc),
        datetime.datetime(2001, 1, 1, 13, 00): datetime.datetime(
            2001, 1, 1, 13, 00, tzinfo=timezone.utc
        ),
        datetime.datetime(2001, 1, 1, 13, 00, tzinfo=timezone.utc): datetime.datetime(
            2001, 1, 1, 13, 00, tzinfo=timezone.utc
        ),
    }
    invalid_inputs = {
        "abc": ["Not a valid datetime."],
        "2001-99-99T99:00": ["Not a valid datetime."],
        "2018-08-16 22:00-24:00": ["Not a valid datetime."],
        datetime.date(2001, 1, 1): ["Expected a datetime but got a date."],
        "9999-12-31T21:59:59.99990-03:00": ["Datetime value out of range."],
    }
    outputs = {
        datetime.datetime(2001, 1, 1, 13, 00): "2001-01-01T13:00:00Z",
        datetime.datetime(
            2001, 1, 1, 13, 00, tzinfo=timezone.utc
        ): "2001-01-01T13:00:00Z",
        "2001-01-01T00:00:00": "2001-01-01T00:00:00",
        str("2016-01-10T00:00:00"): "2016-01-10T00:00:00",
        None: None,
        "": None,
    }
    field = dt.DateTimeField(default_timezone=timezone.utc)


class TestCustomInputFormatDateTimeField(FieldValues):
    """
    Valid and invalid values for `DateTimeField` with a custom input format.
    """

    valid_inputs = {
        "1:35pm, 1 Jan 2001": datetime.datetime(
            2001, 1, 1, 13, 35, tzinfo=timezone.utc
        ),
    }
    invalid_inputs = {"2001-01-01T20:50": ["Not a valid datetime."]}
    outputs = {}
    field = dt.DateTimeField(
        default_timezone=timezone.utc, input_formats=["%I:%M%p, %d %b %Y"]
    )


class TestCustomOutputFormatDateTimeField(FieldValues):
    """
    Values for `DateTimeField` with a custom output format.
    """

    valid_inputs = {}
    invalid_inputs = {}
    outputs = {
        datetime.datetime(2001, 1, 1, 13, 00): "01:00PM, 01 Jan 2001",
    }
    field = dt.DateTimeField(format="%I:%M%p, %d %b %Y")


class TestNoOutputFormatDateTimeField(FieldValues):
    """
    Values for `DateTimeField` with no output format.
    """

    valid_inputs = {}
    invalid_inputs = {}
    outputs = {
        datetime.datetime(2001, 1, 1, 13, 00): datetime.datetime(2001, 1, 1, 13, 00),
    }
    field = dt.DateTimeField(format=None)


class TestCustomOutputFormatDateField(FieldValues):
    """
    Values for `DateField` with a custom output format.
    """

    valid_inputs = {}
    invalid_inputs = {}
    outputs = {datetime.date(2001, 1, 1): "01 Jan 2001"}
    field = dt.DateField(format="%d %b %Y")


class TestTimeField(FieldValues):
    """
    Valid and invalid values for `TimeField`.
    """

    valid_inputs = {
        "13:00": datetime.time(13, 00),
        datetime.time(13, 00): datetime.time(13, 00),
    }
    invalid_inputs = {
        "abc": ["Not a valid time."],
        "99:99": ["Not a valid time."],
    }
    outputs = {
        datetime.time(13, 0): "13:00:00",
        datetime.time(0, 0): "00:00:00",
        "00:00:00": "00:00:00",
        None: None,
        "": None,
    }
    field = dt.TimeField()


class TestCustomInputFormatTimeField(FieldValues):
    """
    Valid and invalid values for `TimeField` with a custom input format.
    """

    valid_inputs = {
        "1:00pm": datetime.time(13, 00),
    }
    invalid_inputs = {
        "13:00": ["Not a valid time."],
    }
    outputs = {}
    field = dt.TimeField(input_formats=["%I:%M%p"])


class TestCustomOutputFormatTimeField(FieldValues):
    """
    Values for `TimeField` with a custom output format.
    """

    valid_inputs = {}
    invalid_inputs = {}
    outputs = {datetime.time(13, 00): "01:00PM"}
    field = dt.TimeField(format="%I:%M%p")


class TestNoOutputFormatTimeField(FieldValues):
    """
    Values for `TimeField` with a no output format.
    """

    valid_inputs = {}
    invalid_inputs = {}
    outputs = {datetime.time(13, 00): datetime.time(13, 00)}
    field = dt.TimeField(format=None)


class TestChoiceField(FieldValues):
    """
    Valid and invalid values for `ChoiceField`.
    """

    valid_inputs = {
        "poor": "poor",
        "medium": "medium",
        "good": "good",
    }
    invalid_inputs = {"amazing": ['"amazing" is not a valid choice.']}
    outputs = {
        "good": {"value": "good", "display": "Good quality"},
        "": "",
        "amazing": {"display": "amazing", "value": "amazing"},
    }
    field = dt.ChoiceField(
        choices=[
            ("poor", "Poor quality"),
            ("medium", "Medium quality"),
            ("good", "Good quality"),
        ]
    )

    def test_allow_blank(self):
        """
        If `allow_blank=True` then '' is a valid input.
        """
        field = dt.ChoiceField(
            allow_blank=True,
            choices=[
                ("poor", "Poor quality"),
                ("medium", "Medium quality"),
                ("good", "Good quality"),
            ],
        )
        output = field.run_validation("", self.context)
        assert output == ""


class TestChoiceFieldWithType(FieldValues):
    """
    Valid and invalid values for a `Choice` field that uses an integer type,
    instead of a char type.
    """

    valid_inputs = {
        "1": 1,
        3: 3,
    }
    invalid_inputs = {
        5: ['"5" is not a valid choice.'],
        "abc": ['"abc" is not a valid choice.'],
    }
    outputs = {
        "1": {"display": "Poor quality", "value": 1},
        1: {"display": "Poor quality", "value": 1},
    }
    field = dt.ChoiceField(
        choices=[
            (1, "Poor quality"),
            (2, "Medium quality"),
            (3, "Good quality"),
        ]
    )


class TestChoiceFieldWithListChoices(FieldValues):
    """
    Valid and invalid values for a `Choice` field that uses a flat list for the
    choices, rather than a list of pairs of (`value`, `description`).
    """

    valid_inputs = {
        "poor": "poor",
        "medium": "medium",
        "good": "good",
    }
    invalid_inputs = {"awful": ['"awful" is not a valid choice.']}
    outputs = {"good": {"display": "good", "value": "good"}}
    field = dt.ChoiceField(choices=("poor", "medium", "good"))


class TestMultipleChoiceField(FieldValues):
    """
    Valid and invalid values for `MultipleChoiceField`.
    """

    valid_inputs = {
        (): set(),
        ("aircon",): {"aircon"},
        ("aircon", "manual"): {"aircon", "manual"},
    }
    invalid_inputs = {
        "abc": ['Expected a list of items but got type "str".'],
        ("aircon", "incorrect"): ['"incorrect" is not a valid choice.'],
    }
    outputs = [(["aircon", "manual", "incorrect"], {"aircon", "manual", "incorrect"})]
    field = dt.MultipleChoiceField(
        choices=[
            ("aircon", "AirCon"),
            ("manual", "Manual drive"),
            ("diesel", "Diesel"),
        ]
    )


class TestEmptyMultipleChoiceField(FieldValues):
    """
    Invalid values for `MultipleChoiceField(allow_empty=False)`.
    """

    valid_inputs = {}
    invalid_inputs = (([], ["This selection may not be empty."]),)
    outputs = []
    field = dt.MultipleChoiceField(
        choices=[
            ("consistency", "Consistency"),
            ("availability", "Availability"),
            ("partition", "Partition tolerance"),
        ],
        allow_empty=False,
    )


class TestBooleanField(FieldValues):
    """
    Valid and invalid values for `BooleanField`.
    """

    valid_inputs = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        1: True,
        0: False,
        True: True,
        False: False,
    }
    invalid_inputs = {
        "foo": ["Not a valid boolean."],
        None: ["This field may not be null."],
    }
    outputs = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        1: True,
        0: False,
        True: True,
        False: False,
        "other": True,
    }
    field = dt.BoolField()

    def test_disallow_unhashable_collection_types(self):
        inputs = (
            [],
            {},
        )
        field = self.field
        for input_value in inputs:
            with pytest.raises(ValidationError) as exc_info:
                field.run_validation(input_value, self.context)
            expected = ["Not a valid boolean."]
            assert exc_info.value.detail == expected


class TestNullBooleanField(TestBooleanField):
    """
    Valid and invalid values for `NullBooleanField`.
    """

    valid_inputs = {
        "true": True,
        "false": False,
        "null": None,
        True: True,
        False: False,
        None: None,
    }
    invalid_inputs = {
        "foo": ["Not a valid boolean."],
    }
    outputs = {
        "true": True,
        "false": False,
        "null": None,
        True: True,
        False: False,
        "other": True,
    }
    field = dt.BoolField(allow_null=True)


class TestListField(FieldValues):
    """
    Values for `ListField` with IntegerField as child.
    """

    valid_inputs = [([1, 2, 3], [1, 2, 3]), (["1", "2", "3"], [1, 2, 3]), ([], [])]
    invalid_inputs = [
        ("not a list", ['Expected a list of items but got type "str".']),
        (
            [1, 2, "error", "error"],
            {2: ["A valid integer is required."], 3: ["A valid integer is required."]},
        ),
        ({"one": "two"}, ['Expected a list of items but got type "dict".']),
    ]
    outputs = [([1, 2, 3], [1, 2, 3]), (["1", "2", "3"], [1, 2, 3])]
    field = dt.ArrayField(child=dt.IntField())

    def test_collection_types_are_invalid_input(self):
        field = dt.ArrayField(child=dt.StrField())
        input_value = {"one": "two"}

        with pytest.raises(ValidationError) as exc_info:
            field.deserialize(input_value, self.context)
        assert exc_info.value.detail == [
            'Expected a list of items but got type "dict".'
        ]


class TestNestedArrayField(FieldValues):
    """
    Values for nested `ArrayField` with IntegerField as child.
    """

    valid_inputs = [([[1, 2], [3]], [[1, 2], [3]]), ([[]], [[]])]
    invalid_inputs = [
        (["not a list"], {0: ['Expected a list of items but got type "str".']}),
        (
            [[1, 2, "error"], ["error"]],
            {
                0: {2: ["A valid integer is required."]},
                1: {0: ["A valid integer is required."]},
            },
        ),
        ([{"one": "two"}], {0: ['Expected a list of items but got type "dict".']}),
    ]
    outputs = [
        ([[1, 2], [3]], [[1, 2], [3]]),
    ]
    field = dt.ArrayField(child=dt.ArrayField(child=dt.IntField()))


class TestEmptyArrayField(FieldValues):
    """
    Values for `ArrayField` with allow_empty=False flag.
    """

    valid_inputs = {}
    invalid_inputs = [([], ["This list may not be empty."])]
    outputs = {}
    field = dt.ArrayField(child=dt.IntField(), allow_empty=False)


class TestArrayFieldLengthLimit(FieldValues):
    valid_inputs = ()
    invalid_inputs = [
        ((0, 1), ["Must have at least 3 items."]),
        ((0, 1, 2, 3, 4, 5), ["Must have no more than 4 items."]),
    ]
    outputs = ()
    field = dt.ArrayField(child=dt.IntField(), min_items=3, max_items=4)


class TestArrayFieldExactLength(FieldValues):
    valid_inputs = ()
    invalid_inputs = [
        ((0, 1), ["Must have 3 items."]),
    ]
    outputs = ()
    field = dt.ArrayField(child=dt.IntField(), exact_items=3)


class TestDictField(FieldValues):
    """
    Values for `DictField` with CharField as child.
    """

    valid_inputs = [
        ({"a": 1, "b": "2", 3: 3}, {"a": "1", "b": "2", "3": "3"}),
        ({}, {}),
    ]
    invalid_inputs = [
        (
            {"a": 1, "b": None, "c": None},
            {
                "b": ["This field may not be null."],
                "c": ["This field may not be null."],
            },
        ),
        ("not a dict", ['Expected a dict of items but got type "str".']),
    ]
    outputs = [
        ({"a": 1, "b": "2", 3: 3}, {"a": "1", "b": "2", "3": "3"}),
    ]
    field = dt.DictField(child=dt.StrField())

    def test_allow_null(self):
        """
        If `allow_null=True` then `None` is a valid input.
        """
        field = dt.DictField(allow_null=True)
        output = field.run_validation(None, self.context)
        assert output is None

    def test_allow_empty_disallowed(self):
        """
        If allow_empty is False then an empty dict is not a valid input.
        """
        field = dt.DictField(allow_empty=False)
        with pytest.raises(ValidationError) as exc_info:
            field.run_validation({}, self.context)

        assert exc_info.value.detail == ["This dict may not be empty."]


class TestJSONField(FieldValues):
    """
    Values for `JSONField`.
    """

    valid_inputs = [
        (
            {"a": 1, "b": ["some", "list", True, 1.23], "3": None},
            {"a": 1, "b": ["some", "list", True, 1.23], "3": None},
        ),
    ]
    invalid_inputs = [
        ({"a": set()}, ["Not a valid JSON."]),
    ]
    outputs = [
        (
            {"a": 1, "b": ["some", "list", True, 1.23], "3": 3},
            {"a": 1, "b": ["some", "list", True, 1.23], "3": 3},
        ),
    ]
    field = dt.JSONField()


class TestConstantField(FieldValues):
    """
    Values for `ConstantField`.
    """

    field = dt.ConstantField(constant="abc")

    valid_inputs = {
        "abc": "abc",
    }
    invalid_inputs = {"abcd": ['Must be "abc".']}
    outputs = {"abc": "abc"}

    def test_disallow_null_constant(self):
        field = dt.ConstantField(constant=None)
        with pytest.raises(ValidationError) as exc_info:
            field.run_validation({}, self.context)

        assert exc_info.value.detail == ["Must be None."]


class MockFile:
    def __init__(self, name="", size=0, url=""):
        self.name = name
        self.size = size
        self.url = url

    def __eq__(self, other):
        return (
            isinstance(other, MockFile)
            and self.name == other.name
            and self.size == other.size
            and self.url == other.url
        )


class TestFileField(FieldValues):
    """
    Values for `FileField`.
    """

    valid_inputs = [
        (MockFile(name="example", size=10), MockFile(name="example", size=10))
    ]
    invalid_inputs = [
        (
            "invalid",
            ["The submitted data was not a file. Check the encoding type on the form."],
        ),
        (MockFile(name="example.txt", size=0), ["The submitted file is empty."]),
        (MockFile(name="", size=10), ["No filename could be determined."]),
        (
            MockFile(name="x" * 100, size=10),
            ["Ensure this filename has at most 10 characters (it has 100)."],
        ),
    ]
    outputs = [
        (MockFile(name="example.txt", url="/example.txt"), "/example.txt"),
        ("", None),
    ]
    field = dt.FileField(max_length=10)


class TestMethodField:
    def test_method_field(self):
        class ExampleSerializer(dt.Serializer):
            example_field = dt.MethodField()

            def get_example_field(self, obj):
                return "ran get_example_field(%d)" % obj["example_field"]

        serializer = ExampleSerializer({"example_field": 123})
        assert serializer.data == {"example_field": "ran get_example_field(123)"}

    def test_redundant_method_name(self):
        class ExampleSerializer(dt.Serializer):
            example_field = dt.MethodField("get_example_field")

        field = ExampleSerializer().fields["example_field"]
        assert field.method_name == "get_example_field"


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


class MockQueryset:
    def __init__(self, iterable):
        self.items = iterable

    def __getitem__(self, val):
        return self.items[val]

    def get(self, **lookup):
        for item in self.items:
            if all(
                [getattr(item, key, None) == value for key, value in lookup.items()]
            ):
                return item
        raise ObjectDoesNotExist()


class BadType:
    """
    When used as a lookup with a `MockQueryset`, these objects
    will raise a `TypeError`, as occurs in Django when making
    queryset lookups with an incorrect type for the lookup value.
    """

    def __eq__(self):
        raise TypeError()


class TestRelatedField(APISimpleTestCase):
    context = {}

    def setUp(self):
        self.queryset = MockQueryset(
            [
                MockObject(pk=1, name="foo"),
                MockObject(pk=2, name="bar"),
                MockObject(pk=3, name="baz"),
            ]
        )
        self.instance = self.queryset.items[2]
        self.field = dt.RelatedField(queryset=self.queryset)

    def test_pk_related_lookup_exists(self):
        instance = self.field.deserialize(self.instance.pk, self.context)
        assert instance is self.instance

    def test_pk_related_lookup_does_not_exist(self):
        with pytest.raises(ValidationError) as excinfo:
            self.field.deserialize(4, self.context)
        msg = excinfo.value.detail[0]
        assert msg == 'Invalid pk "4" - object does not exist.'

    def test_pk_related_lookup_invalid_type(self):
        with pytest.raises(ValidationError) as excinfo:
            self.field.deserialize(BadType(), self.context)
        msg = excinfo.value.detail[0]
        assert msg == "Incorrect type. Expected pk value, received BadType."

    def test_pk_related_lookup_bool(self):
        with pytest.raises(ValidationError) as excinfo:
            self.field.deserialize(True, self.context)
        msg = excinfo.value.detail[0]
        assert msg == "Incorrect type. Expected pk value, received bool."


class TestManyRelatedField(APISimpleTestCase):
    context = {}

    def setUp(self):
        self.queryset = MockQueryset(
            [
                MockObject(pk=1, name="foo"),
                MockObject(pk=2, name="bar"),
                MockObject(pk=3, name="baz"),
            ]
        )
        self.child_relation = dt.RelatedField(queryset=self.queryset)
        self.instance = self.queryset.items[2]
        self.field = dt.ManyRelatedField(
            child_relation=self.child_relation, allow_empty=False
        )

    def test_serialize(self):
        data = self.field.serialize(self.queryset, self.context)
        assert data == [1, 2, 3]

    def test_deserialize(self):
        data = self.field.deserialize([1, 2, 3], self.context)
        assert data == self.queryset.items

    def test_child_relation_is_list(self):
        with pytest.raises(ValidationError) as excinfo:
            self.field.deserialize(self.instance, self.context)
        msg = excinfo.value.detail[0]
        assert msg == 'Expected a list of items but got type "MockObject".'

    def test_child_relation_is_not_empty(self):
        with pytest.raises(ValidationError) as excinfo:
            self.field.deserialize([], self.context)
        msg = excinfo.value.detail[0]
        assert msg == "This list may not be empty."
