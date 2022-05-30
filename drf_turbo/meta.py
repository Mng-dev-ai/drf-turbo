from django.db import models

from drf_turbo.fields import (ArrayField, BoolField, ChoiceField, DateField,
                              DateTimeField, DecimalField, EmailField, Field,
                              FileField, FloatField, IntField, IPField,
                              JSONField, ManyRelatedField, RelatedField,
                              StrField, TimeField, URLField, UUIDField)

try:
    from django.contrib.postgres import fields as postgres_fields

except ImportError:
    postgres_fields = None


class SerializerMetaclass(type):
    @classmethod
    def _get_fields(cls, bases, attrs):
        fields = [
            (field_name, attrs.pop(field_name))
            for field_name, obj in list(attrs.items())
            if isinstance(obj, Field)
        ]
        for base in reversed(bases):
            if hasattr(base, "_fields"):
                fields = list(getattr(base, "_fields").items()) + fields
        return dict(fields)

    def __new__(cls, name, bases, attrs):
        attrs["_fields"] = cls._get_fields(bases, attrs)
        return super().__new__(cls, name, bases, attrs)


class ModelSerializerMetaclass(SerializerMetaclass):

    TYPE_MAPPING = {
        models.AutoField: IntField,
        models.BigIntegerField: IntField,
        models.BooleanField: BoolField,
        models.CharField: StrField,
        models.DateField: DateField,
        models.TimeField: TimeField,
        models.DateTimeField: DateTimeField,
        models.EmailField: EmailField,
        models.FileField: FileField,
        models.FloatField: FloatField,
        models.ImageField: FileField,
        models.IntegerField: IntField,
        models.NullBooleanField: BoolField,
        models.PositiveIntegerField: IntField,
        models.PositiveSmallIntegerField: IntField,
        models.SmallIntegerField: IntField,
        models.TextField: StrField,
        models.URLField: URLField,
        models.GenericIPAddressField: IPField,
        models.JSONField: JSONField,
        models.UUIDField: UUIDField,
    }

    if postgres_fields is not None:
        TYPE_MAPPING[postgres_fields.ArrayField] = ArrayField
        TYPE_MAPPING[postgres_fields.JSONField] = JSONField

    @staticmethod
    def _get_implicit_fields(model_fields, fields, exclude):

        if fields == "__all__":
            fields = model_fields
        elif fields and isinstance(fields, (list, tuple)):
            fields = [field for field in model_fields if field.name in fields]

        elif not fields and exclude:
            fields = [field for field in model_fields if field.name not in exclude]
        # this implicitly handles the case when `fields` is set and `exclude`
        # isn't. Then all fields declared will be returned without any
        # modification.
        return fields

    @staticmethod
    def _filter_fields(cls, declared_fields, explicit_fields, implicit_fields):
        for field in implicit_fields:
            if field.name not in explicit_fields:
                klass = field.__class__
                if issubclass(klass, (models.ForeignKey, models.OneToOneField)):
                    field_obj = RelatedField()
                    field_obj.queryset = field.related_model.objects
                elif issubclass(klass, models.ManyToManyField):
                    field_obj = ManyRelatedField()
                    child_obj = RelatedField()
                    child_obj.queryset = field.related_model.objects
                    field_obj.child_relation = child_obj
                elif issubclass(klass, models.DecimalField):
                    field_obj = DecimalField(
                        max_digits=field.max_digits, decimal_places=field.decimal_places
                    )
                else:
                    try:
                        field.get_choices()
                        field_obj = ChoiceField(choices=field.choices)
                    except Exception:
                        field_obj = cls.TYPE_MAPPING.get(klass, Field)()

                field_obj.attr = field.name
                field_obj.help_text = str(field.help_text)
                field_obj.validators = field.validators
                if issubclass(klass, models.AutoField) or not field.editable:
                    field_obj.read_only = True
                if field.has_default() or field.blank or field.null:
                    field_obj.required = False
                if field.get_internal_type() == "TextField":
                    field_obj.default_value = ""
                if field.has_default():
                    field_obj.default_value = (
                        field.default.value
                        if hasattr(field.default, "value")
                        else field.default
                    )
                if getattr(field, "auto_now", False):
                    field_obj.default_value = field.auto_now
                if getattr(field, "auto_now_add", False):
                    field_obj.default_value = field.auto_now_add

                declared_fields[field.name] = field_obj

        return declared_fields

    @staticmethod
    def _read_only_fields(read_only_fields, declared_fields):
        if read_only_fields:
            if not isinstance(read_only_fields, (list, tuple)):
                raise TypeError(
                    "The `read_only_fields` option must be a list or tuple. "
                    "Got %s." % type(read_only_fields).__name__
                )
            for field in read_only_fields:
                declared_fields[field].read_only = True
                declared_fields[field].required = False

    @staticmethod
    def _write_only_fields(write_only_fields, declared_fields):
        if write_only_fields:
            if not isinstance(write_only_fields, (list, tuple)):
                raise TypeError(
                    "The `write_only_fields` option must be a list or tuple. "
                    "Got %s." % type(write_only_fields).__name__
                )
            for field in write_only_fields:
                declared_fields[field].write_only = True

    def __new__(cls, name, bases, attrs):
        klass = super().__new__(cls, name, bases, attrs)
        declared_fields = attrs["_fields"]
        meta = getattr(klass, "Meta", None)
        if meta:
            model = getattr(meta, "model", None)
            fields = getattr(meta, "fields", None)
            exclude = getattr(meta, "exclude", None)
            read_only_fields = getattr(meta, "read_only_fields", None)
            write_only_fields = getattr(meta, "write_only_fields", None)
            if not model:
                raise RuntimeError(
                    "If you specifiy a Meta class, you need to atleast specify a model"
                )
            if not fields and not exclude:
                raise RuntimeError(
                    "You need to specifiy either `fields` or `exclude` in Meta"
                )
            if fields and exclude:
                raise RuntimeError("`fields` and `exclude` prohibit each other.")

            if hasattr(model, "_meta"):
                # Django models
                model_fields = [field for field in model._meta.fields]
                many_to_many_fields = [field for field in model._meta.many_to_many]
                model_fields.extend(many_to_many_fields)
                implicit_fields = cls._get_implicit_fields(
                    model_fields, fields, exclude
                )
                explicit_fields = declared_fields.keys()
                declared_fields = cls._filter_fields(
                    cls, declared_fields, explicit_fields, implicit_fields
                )
                cls._read_only_fields(read_only_fields, declared_fields)
                cls._write_only_fields(write_only_fields, declared_fields)

                klass._model_fields = model_fields
        klass._fields = declared_fields

        return klass
