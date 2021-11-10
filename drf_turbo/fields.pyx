cimport cython

from drf_turbo.utils import is_iterable_and_not_string,get_error_detail,is_collection,get_attribute
from drf_turbo.exceptions import *
from django.core.validators import EmailValidator,URLValidator,RegexValidator,MaxLengthValidator,MinLengthValidator,MinValueValidator,MaxValueValidator,ProhibitNullCharactersValidator
from django.core.exceptions import ValidationError as DjangoValidationError
import ipaddress
import copy
import json
from django.core.exceptions import ObjectDoesNotExist
import uuid
from django.utils.dateparse import (
    parse_date, parse_datetime, parse_time
)
import decimal,re
from django.utils.encoding import  smart_str
from rest_framework.settings import api_settings
import datetime
from rest_framework import (
    ISO_8601
)
from django.conf import settings
from django.utils import timezone
from django.utils.timezone import utc
from pytz.exceptions import InvalidTimeError

cdef object NO_DEFAULT = object()


cdef class SkipField(Exception):
    pass


cdef class Field :
    """
    Basic field from which other fields should extend. It applies no
    formatting by default, and should only be used in cases where
    data does not need to be formatted before being serialized or deserialized.
    On error, the name of the field will be returned.

    :param str attr:  The name of the attribute to get the value from when serializing.
    :param bool call: Whether the value should be called after it is retrieved
        from the object. Useful if an object has a method to be serialized. 
    :param bool required: Raise a `ValidationError` if the field value
        is not supplied during deserialization.      
    :param bool write_only: If `True` skip this field during serialization, otherwise
        its value will be present in the serialized data.      
    :param bool read_only: If `True` skip this field during deserialization, otherwise
        its value will be present in the deserialized object.  
    :param str label: A label to use as the name of the serialized field
        instead of using the attribute name of the field.   
    :param list validators: A list of validators to apply against incoming data during deserialization.     
    :param str field_name: The name of field.  
    :param str root: The root(parent) of field.   
    :param default_value: Default value to be used during serialization and deserialization.
    :param initial: The initial value for the field.
    """

    is_method_field = False
    default_error_messages = {
        'required': 'This field is required.',
        'null': 'This field may not be null.',
        }
    _initial = None

    def __init__(
        self,
        basestring attr = None,
        bint call= False,
        bint required= True,
        bint write_only = False,
        bint read_only = False,
        bint allow_null = False,
        basestring label = None,
        basestring help_text = None,
        dict style = None ,
        object validators = None,
        object default_value  = NO_DEFAULT,
        object initial = NO_DEFAULT,
        basestring field_name = None,
        object root = None ,
        dict error_messages = None,
        
    ): 
        required = False if default_value is not NO_DEFAULT else required
        assert not (read_only and write_only), 'May not set both `read_only` and `write_only`'
        assert not (required and default_value is not NO_DEFAULT), 'May not set both `required` and `default_value`'

        self.attr = attr
        self.call = call
        self.required = required
        self.write_only = write_only
        self.read_only = (read_only or call or
                          (attr is not None and '.' in attr)) # type: ignore
        self.allow_null = allow_null
        self.label = label
        self.default_value = default_value
        self.initial = self._initial if (initial is NO_DEFAULT) else initial
        self.help_text = help_text
        self.style = {} if style is None else style
        self.field_name = field_name
        self.root = root
        if validators is None:
            self.validators = []
        elif callable(validators):
            self.validators = [validators]
        elif is_iterable_and_not_string(validators) :
            self.validators = list(validators)
        else:
            raise ValueError(
                "The 'validators' parameter must be a callable "
                "or a collection of callables."
            )

        messages = {}
        for cls in reversed(self.__class__.__mro__):
            messages.update(getattr(cls, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

    def raise_if_fail(self, key: str, **kwargs) :
        """Helper method to make a `ValidationError` with an error message
        from ``self.error_messages``.
        """
        try:
            msg = self.error_messages[key]
        except KeyError as error:
            raise AssertionError(error)
        if isinstance(msg, (str, bytes)):
            msg = msg.format(**kwargs)
        return ValidationError(msg)

        
    cpdef serialize(self,value, dict context):
        """
        Transform the *outgoing* native value into primitive data

        :param value: The outgoing value.
        :param context: The context for the request.
        """
        return value
    
    
    cpdef deserialize(self,data, dict context):
        """
        Transform the *incoming* primitive data into a native value.
        
        :param data: The incoming data.
        :param context: The context for the request.
        """
        return data
    

    cpdef method_getter(self,field_name, root) :
        """
        Returns a function that fetches an attribute from an object.

        :field_name: The name of the attribute to get.
        :root: The root of the field.
        """
        return None
        
        
    cpdef void bind(self,basestring field_name, object root):
        """
        Update the field name and root for the field instance.

        :field_name: The name of the field.
        :root: The root of the field.
        """
        self.field_name = field_name
        self.root = root
        if self.label is None:
            self.label = field_name.replace('_', ' ').capitalize()

        if self.attr is None:
            self.attr = field_name

        self.attrs = self.attr.split('.') if self.attr else []


    cpdef get_default_value(self):
        """
        Return the default value for this field.
        """
        if self.default_value is NO_DEFAULT or getattr(self.root, 'partial', False):
            raise SkipField()
        if callable(self.default_value):
            return self.default_value()
        return self.default_value

    cpdef get_initial(self):
        """
        Return the initial value for this field.
        """
        if callable(self.initial):
            return self.initial()
        return self.initial

    cpdef get_attribute(self, instance , attr=None):
        """
        Return the value of the field from the provided instance.
        """
        try:
            if attr is None:
                return get_attribute(instance, self.attrs)
            return get_attribute(instance, attr)
        except (KeyError, AttributeError) as exc:
            if self.default_value is not NO_DEFAULT:
                return self.get_default_value()
            if self.allow_null:
                return None
            if not self.required:
                raise SkipField()
            msg = (
                'Got {exc_type} when attempting to get a value for field'
            )
            raise type(exc)(msg)

    cpdef validate_empty_values(self, data):
        """
        Validate empty values, and either:
        * Raise `ValidationError`, indicating invalid data.
        * Return (True, data), indicating an empty value that should be
          returned without any further validation being applied.
        * Return (False, data), indicating a non-empty value, that should
          have validation applied as normal.
        """
        if self.read_only:
            return (True, self.get_default_value())

        if data is NO_DEFAULT:
            if getattr(self.root, 'partial', False):
                raise SkipField()
            if self.required:
                raise ValidationError('This field is required.')
            return (True, self.get_default_value())

        if data is None:
            if not self.allow_null:
                raise ValidationError('This field may not be null.')
            return (True, None)

        return (False, data)

    cpdef run_validation(self,object data,dict context) :
        """
        Validate an input data.
        """

        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data
        value = self.deserialize(data,context)
        self.validate_or_raise(value)
        return value
    
    
    cpdef long validate_or_raise(self,value) except -1 :
        """
        Validate the value and raise a `ValidationError` if validation fails.
        """

        cdef list errors = []
        for validator in self.validators :
            try :
                validator(value)
            except ValidationError as exc:
                if isinstance(exc.detail, dict):
                    raise   
                errors.extend(exc.detail)
            except DjangoValidationError as exc:
                errors.extend(get_error_detail(exc))
        if errors:
            raise ValidationError(errors)
        
        


        
cdef class StrField(Field):
    """"
    A field that validates input as an string.

    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """
    
    default_error_messages = {
        'blank': 'May not be blank.',
        'invalid': 'Not a valid string.'
    }    
    _initial = ''
    def __init__(self,**kwargs) :
        self.allow_blank = kwargs.pop('allow_blank', False)
        self.trim_whitespace = kwargs.pop('trim_whitespace', True)
        self.max_length = kwargs.pop('max_length', None)
        self.min_length = kwargs.pop('min_length', None)
        super().__init__(**kwargs)
        if self.max_length is not None:
            self.validators.append(
                MaxLengthValidator(self.max_length))
        if self.min_length is not None:
            self.validators.append(MinLengthValidator(self.min_length))
        self.validators.append(ProhibitNullCharactersValidator())

         
    cpdef serialize(self,value,dict context) :
        return str(value)

    cpdef deserialize(self,data,dict context) :
        if data == '' or (self.trim_whitespace and str(data).strip() == ''):
            if not self.allow_blank:
                raise self.raise_if_fail('blank')
        if isinstance(data, bool) or not isinstance(data, (str, int, float,)):
           raise self.raise_if_fail('invalid')
        data = str(data)
        return data.strip() if self.trim_whitespace else data
    
@cython.final
cdef class EmailField(StrField):
    """
    A field that validates input as an E-Mail address.

    :param to_lower: If True, convert the value to lowercase before validating.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """

    default_error_messages = {
        'invalid': 'Enter a valid email address.'
    }
    def __init__(self, **kwargs): 
        self.to_lower = kwargs.pop('to_lower', False)
        super().__init__(**kwargs)
        validator = EmailValidator(message=self.error_messages['invalid'])
        self.validators.append(validator)
        
    cpdef inline serialize(self,value,dict context):
        if self.to_lower :
            return value.lower()
        return value
    
    cpdef inline deserialize(self,data,dict context):
        if self.to_lower :
            return data.lower()
        return data

@cython.final
cdef class URLField(StrField):
    """
    A field that validates input as an URL.

    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """

    default_error_messages = {
        'invalid': 'Enter a valid URL.'
    }

    def __init__(self, **kwargs): 
        super().__init__(**kwargs)
        validator = URLValidator(message=self.error_messages['invalid'])
        self.validators.append(validator)

@cython.final
cdef class RegexField(StrField):
    """
    A field that validates input against a given regular expression.

    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """

    default_error_messages = {
        'invalid': 'This value does not match the required pattern.'
    }

    def __init__(self, regex, **kwargs):
        super().__init__(**kwargs)
        validator = RegexValidator(regex, message=self.error_messages['invalid'])
        self.validators.append(validator)

@cython.final
cdef class IPField(StrField):
    """
    A field that validates that input is an IP address.

    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """

    default_error_messages = {
        'invalid': 'Enter a valid IPv4 or IPv6 address.',
    }
        
    cpdef inline deserialize(self,data,dict context):
        try:
           return ipaddress.ip_address(data)
        except (ValueError, TypeError) :
            raise self.raise_if_fail('invalid')
        
@cython.final
cdef class PasswordField(StrField):
    """
    A field that validates input as a password.

    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """

    def __init__(self,**kwargs):
        kwargs['write_only'] = True
        kwargs['min_length'] = 4
        kwargs['required'] = True
        super().__init__(**kwargs)


@cython.final
cdef class UUIDField(StrField):
    """
    A field that validates input as an UUID.

    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """

    default_error_messages = {
        
        "invalid": "Not a valid UUID."
    }

    cpdef inline deserialize(self,data,dict context):
        if data is None:
            return None
        if isinstance(data, uuid.UUID):
            return data
        try:
            if isinstance(data, bytes) and len(data) == 16:
                return uuid.UUID(bytes=data)
            elif isinstance(data,int):
                return uuid.UUID(int=data)
            elif isinstance(data,str):
                return uuid.UUID(hex=data)
            else:
                return uuid.UUID(data)
        except :
            raise self.raise_if_fail('invalid')

@cython.final
cdef class SlugField(Field):
    """
    Slug field type.

    :param allow_unicode: If True, allow unicode characters in the field.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """
    default_error_messages = {
        'invalid': 'Not a valid slug.',
        'invalid_unicode' : 'Nnot a valid unicode slug.'
    }

    def __init__(self, allow_unicode=False, **kwargs):
        self.allow_unicode = allow_unicode
        super().__init__(**kwargs)
        if self.allow_unicode:
            validator = RegexValidator(re.compile(r'^[-\w]+\Z', re.UNICODE), message=self.error_messages['invalid_unicode'])
        else:
            validator = RegexValidator(re.compile(r'^[-a-zA-Z0-9_]+$'), message=self.error_messages['invalid'])
        self.validators.append(validator)





@cython.final
cdef class IntField(Field):
    """
    A field that validates input as an integer.

    :param min_value: The minimum value allowed.
    :param max_value : The maximum value allowed.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """
    default_error_messages = {
        'invalid': 'A valid integer is required.',
    }
    re_decimal = re.compile(r'\.0*\s*$')  # allow e.g. '1.0' as an int, but not '1.2'
    def __init__(self,**kwargs):
        self.max_value = kwargs.pop('max_value', None)
        self.min_value = kwargs.pop('min_value', None)
        super().__init__(**kwargs)
        if self.max_value is not None:
            self.validators.append(
                MaxValueValidator(self.max_value))
        if self.min_value is not None:
            self.validators.append(
                MinValueValidator(self.min_value))
        
    cpdef inline serialize(self,value,dict context):
        return int(value)

    cpdef inline deserialize(self,data,dict context):
        try:
            data = int(self.re_decimal.sub('', str(data)))
        except (ValueError, TypeError):
            raise self.raise_if_fail('invalid')
        return data

@cython.final
cdef class FloatField(Field):
    """
    A field that validates input as a float.

    :param min_value: The minimum value allowed.
    :param max_value: The maximum value allowed.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """

    default_error_messages = {
        'invalid': 'A valid number is required.',
    }
    
    def __init__(self,**kwargs):
        self.max_value = kwargs.pop('max_value', None)
        self.min_value = kwargs.pop('min_value', None)
        super().__init__(**kwargs)
        if self.max_value is not None:
            self.validators.append(
                MaxValueValidator(self.max_value))
        if self.min_value is not None:
            self.validators.append(
                MinValueValidator(self.min_value))


    cpdef inline serialize(self,value,dict context):
        return float(value)
    
    cpdef inline deserialize(self,data,dict context):
        try:
            return float(data)
        except (TypeError, ValueError):
           raise self.raise_if_fail('invalid')

@cython.final
cdef class DecimalField(Field):
    """
    A field that validates input as a Python Decimal.

    :param max_digits(required): Maximum number of digits.
    :param deciaml_places(required): Number of decimal places.
    :param min_value: The minimum value allowed.
    :param max_value: The maximum value allowed.
    :param coerce_to_string: If True, values will be converted to strings during serialization.
    :param rounding: How to round the value during serialization.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """

    default_error_messages = {
        'invalid': 'A valid number is required.',
        'max_value': 'Ensure this value is less than or equal to {max_value}.',
        'min_value': 'Ensure this value is greater than or equal to {min_value}.',
        'max_digits': 'Ensure that there are no more than {max_digits} digits in total.',
        'max_decimal_places': 'Ensure that there are no more than {max_decimal_places} decimal places.',
        'max_whole_digits': 'Ensure that there are no more than {max_whole_digits} digits before the decimal point.',
        'max_string_length': 'String value too large.'
    }
    MAX_STRING_LENGTH = 1000  # Guard against malicious string inputs.

    def __init__(self, max_digits, decimal_places, max_value=None, min_value=None,coerce_to_string=None,rounding=None,**kwargs):
        self.max_digits = max_digits
        self.decimal_places = decimal_places
        self.max_value = max_value
        self.min_value = min_value
        if self.max_digits is not None and self.decimal_places is not None:
            self.max_whole_digits = self.max_digits - self.decimal_places
        else:
            self.max_whole_digits = None

        if coerce_to_string is None:
            self.coerce_to_string = api_settings.COERCE_DECIMAL_TO_STRING
        else:
            self.coerce_to_string = coerce_to_string

        super().__init__(**kwargs)

        if self.max_value is not None:
            self.validators.append(
                MaxValueValidator(self.max_value))
        if self.min_value is not None:
            self.validators.append(
                MinValueValidator(self.min_value))
      
        if rounding is not None:
            valid_roundings = [v for k, v in vars(decimal).items() if k.startswith('ROUND_')]
            assert rounding in valid_roundings, (
                'Invalid rounding option %s. Valid values for rounding are: %s' % (rounding, valid_roundings))
        self.rounding = rounding


    cpdef inline serialize(self,value,dict context):
        if value is None:
            if self.coerce_to_string:
                return ''
            else:
                return None

        if not isinstance(value, decimal.Decimal):
            value = decimal.Decimal(str(value).strip())

        quantized = self.quantize(value)
        if not self.coerce_to_string:
            return quantized

        return '{:f}'.format(quantized)

      

    cpdef inline deserialize(self,data,dict context):
        """
        Validate that the input is a decimal number and return a Decimal
        instance.
        """

        data = smart_str(data).strip()    

        if data == '' and self.allow_null:
            return None

        if len(data) > self.MAX_STRING_LENGTH:
            raise self.raise_if_fail('max_string_length')

        try:
            value = decimal.Decimal(data)
        except decimal.DecimalException:
            raise self.raise_if_fail('invalid')

        if value.is_nan():
            raise self.raise_if_fail('invalid')

        if value in (decimal.Decimal('Inf'), decimal.Decimal('-Inf')):
            raise self.raise_if_fail('invalid')

        return self.quantize(self.validate_precision(value))

    cdef inline validate_precision(self, value):
        """
        Ensure that there are no more than max_digits in the number, and no
        more than decimal_places digits after the decimal point.
        Override this method to disable the precision validation for input
        values or to enhance it in any way you need to.
        """
        sign, digittuple, exponent = value.as_tuple()

        if exponent >= 0:
            # 1234500.0
            total_digits = len(digittuple) + exponent
            whole_digits = total_digits
            decimal_places = 0
        elif len(digittuple) > abs(exponent):
            # 123.45
            total_digits = len(digittuple)
            whole_digits = total_digits - abs(exponent)
            decimal_places = abs(exponent)
        else:
            # 0.001234
            total_digits = abs(exponent)
            whole_digits = 0
            decimal_places = total_digits

        if self.max_digits is not None and total_digits > self.max_digits:
           raise self.raise_if_fail('max_digits', max_digits=self.max_digits)
        if self.decimal_places is not None and decimal_places > self.decimal_places:
            raise self.raise_if_fail('max_decimal_places', max_decimal_places=self.decimal_places)
        if self.max_whole_digits is not None and whole_digits > self.max_whole_digits:
            raise self.raise_if_fail('max_whole_digits', max_whole_digits=self.max_whole_digits)

        return value

    cdef inline quantize(self, value):
        """
        Quantize the decimal value to the configured precision.
        """
        if self.decimal_places is None:
            return value

        context = decimal.getcontext().copy()
        if self.max_digits is not None:
            context.prec = self.max_digits
        return value.quantize(
            decimal.Decimal('.1') ** self.decimal_places,
            rounding=self.rounding,
            context=context
        )


@cython.final
cdef class BoolField(Field):
    """
    Boolean field type.

    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """
    default_error_messages = {
        'invalid': 'Not a valid boolean.'
    }
    _initial = False
    coerce_values = {
        "true": True,
        "True": True,
        "TRUE": True,
        't' : True,
        "T" : True,
        "on": True,
        "1": True,
        True : True,
        1: True,
        "off": False,
        "f" : False,
        "F" : False,
        "false": False,
        "False":False,
        "FALSE" : False,
        "0": False,
        "": False,
        False : False,
        0: False,
    }
    coerce_null_values = {"", "null","Null","NULL","none","None","NONE"}
        
    cpdef inline serialize(self,value,dict context):
        try:
            if self.allow_null and value in self.coerce_null_values:
                return None
            value = self.coerce_values[value]
        except (KeyError,TypeError):
            pass
        return bool(value)
    
    cpdef inline deserialize(self,data,dict context):
        try:
            if self.allow_null and data in self.coerce_null_values:
                return None
            data = self.coerce_values[data]
        except (KeyError,TypeError):
            raise self.raise_if_fail('invalid')
        return data
    
cdef class ChoiceField(Field):
    """
    Choice field type.

    :param choices(required): A list of valid choices.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """
    default_error_messages = {
        'invalid_choice': '"{input}" is not a valid choice.'
    }

    def __init__(self, choices, **kwargs):
        
        pairs = [
            isinstance(item, (list, tuple)) and len(item) == 2
            for item in choices
        ]
        if all(pairs):
            self.choices = dict([(key, display_value) for key, display_value in choices])
        else:
            self.choices = dict([(item, item) for item in choices])

        self.choice_strings_to_values = dict([
            (str(key), key) for key in self.choices.keys()
        ])
        
        self.choice_strings_to_display = dict([
            (str(key), value) for key,value in self.choices.items()
        ])


        self.allow_blank = kwargs.pop('allow_blank', False)
        super().__init__(**kwargs)

        
        
    cpdef serialize(self,value,dict context):
        if value in ('', None):
            return value
        
        return {
            'value': self.choice_strings_to_values.get(str(value), value),
            'display': self.choice_strings_to_display.get(str(value), value),
        }

        
    cpdef deserialize(self,data,dict context) :
        if data == '' and self.allow_blank:
            return ''
        try:
            return self.choice_strings_to_values[str(data)]
        except:
            raise self.raise_if_fail('invalid_choice', input=data)


@cython.final
cdef class MultipleChoiceField(ChoiceField):
    """
    Multiple choice field type.

    :param allow_empty: If True, allow the user to leave the field blank.
    :param kwargs: The same keyword arguments that :class:`Field` and class:`ChoiceField` receives.
    """
    default_error_messages = {
        'not_a_list': 'Expected a list of items but got type "{input_type}".',
        'empty': 'This selection may not be empty.',
        'invalid_choice': '"{input}" is not a valid choice.'
    }

    def __init__(self, **kwargs):
        self.allow_empty = kwargs.pop('allow_empty', True)
        super().__init__(**kwargs)


    cpdef inline serialize(self,value,dict context):
        return {
            self.choice_strings_to_values.get(str(item), item) for item in value
        }

    cpdef inline deserialize(self,data,dict context) :
        if isinstance(data, str) or not hasattr(data, '__iter__'):
            raise self.raise_if_fail('not_a_list', input_type=type(data).__name__)
        if not self.allow_empty and len(data) == 0:
            raise self.raise_if_fail('empty')

        new_data = set()
        for item in data :
            if item == '' and self.allow_blank:
                return ''
            try:
                new_data.add(self.choice_strings_to_values[str(item)])
            except:
                raise self.raise_if_fail('invalid_choice', input=item)
        return new_data




@cython.final
cdef class DateTimeField(Field):
    """
    A field that (de)serializes to a :class:`datetime.datetime` object. 

    :param format: The format to use when serializing/deserializing.
    :param input_formats: A list of formats to check for when deserializing input.
    :param default_timezone: The timezone to use when creating datetime instances.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """
    default_error_messages = {
        'invalid': 'Not a valid datetime.',
        'date': 'Expected a datetime but got a date.',
        'make_aware':'Invalid datetime for the timezone "{timezone}".',
        'overflow': 'Datetime value out of range.'
    }       
    datetime_parser = datetime.datetime.strptime 

    def __init__(self, format=NO_DEFAULT,input_formats=None,default_timezone=None,**kwargs):
        if format is NO_DEFAULT:
            self.format = api_settings.DATETIME_FORMAT
        else:
            self.format = format
        if input_formats is None:
            self.input_formats = api_settings.DATETIME_INPUT_FORMATS
        else:
            self.input_formats = input_formats

        if default_timezone is None:
            self.timezone = self.get_default_timezone()
        else:
            self.timezone = default_timezone

        super().__init__(**kwargs)

    cpdef inline get_default_timezone(self):
        return timezone.get_current_timezone() if settings.USE_TZ else None


    cpdef inline enforce_timezone(self, value):
        """
        When `self.default_timezone` is `None`, always return naive datetimes.
        When `self.default_timezone` is not `None`, always return aware datetimes.
        """
        if self.timezone is not None:
            if timezone.is_aware(value):
                try:
                    return value.astimezone(self.timezone)
                except OverflowError:
                   raise self.raise_if_fail('overflow')
            try:
                return timezone.make_aware(value, self.timezone)
            except InvalidTimeError:
                raise self.raise_if_fail('make_aware', timezone=self.timezone)
        elif (self.timezone is None) and timezone.is_aware(value):
            return timezone.make_naive(value, utc)
        return value


    cpdef inline serialize(self,value,dict context):
        if not value:
            return None

        if self.format is None or isinstance(value, str):
            return value

        value = self.enforce_timezone(value)

        if self.format.lower() == ISO_8601:
            value = value.isoformat()
            if value.endswith('+00:00'):
                value = value[:-6] + 'Z'
            return value
        return value.strftime(self.format)

    
    cpdef inline deserialize(self,data,dict context) :


        if isinstance(data, datetime.date) and not isinstance(data, datetime.datetime):
            raise self.raise_if_fail('date')

        if isinstance(data, datetime.datetime):
            return self.enforce_timezone(data)

        for input_format in self.input_formats:
            if input_format.lower() == ISO_8601:
                try:
                    parsed = parse_datetime(data)
                    if parsed is not None:
                        return self.enforce_timezone(parsed)
                except (ValueError, TypeError):
                    pass
            else:
                try:
                    parsed = self.datetime_parser(data, input_format)
                    return self.enforce_timezone(parsed)
                except (ValueError, TypeError):
                    pass

        raise self.raise_if_fail('invalid')
            
@cython.final
cdef class DateField(Field):
    """
    A field that (de)serializes to a :class:`datetime.date` object.
    
    :param format: Either ``"%Y-%m-%d"`` or ``"%m/%d/%Y"``, or a custom
        string of the format passed to ``strftime``.
    :param input_formats: A list of strings, or a custom list of input formats
        to be used to parse the input date string.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """

    default_error_messages = {
        'invalid': 'Not a valid date.',
        'datetime': 'Expected a date but got a datetime.',
    }

    def __init__(self, format=None,input_formats=None,**kwargs):
        if format is None:
            self.format = api_settings.DATE_FORMAT
        else:
            self.format = format

        if input_formats is None:
            self.input_formats = api_settings.DATE_INPUT_FORMATS
        else:
            self.input_formats = input_formats

        super().__init__(**kwargs)


    cpdef inline serialize(self, value,dict context):
        if not value:
            return None
        if isinstance(value, str):
            return value
        assert not isinstance(value, datetime.datetime), (
            'Expected a `date`, but got a `datetime`. Refusing to coerce, '
            'as this may mean losing timezone information. Use a custom '
            'read-only field and deal with timezone issues explicitly.'
        )

        if self.format.lower() == ISO_8601:
            return value.isoformat()

        return value.strftime(self.format)


    cpdef inline deserialize(self, data,dict context) :

        if isinstance(data, datetime.datetime):
            raise self.raise_if_fail('datetime')

        if isinstance(data, datetime.date):
            return data

        for input_format in self.input_formats:
            if input_format.lower() == ISO_8601:
                try:
                    parsed = parse_date(data)
                except (ValueError, TypeError):
                    pass
                else:
                    if parsed is not None:
                        return parsed
            else:
                try:
                    parsed = self.datetime_parser(data, input_format)
                except (ValueError, TypeError):
                    pass
                else:
                    return parsed.date()

        raise self.raise_if_fail('invalid')


@cython.final
cdef class TimeField(Field):
    """
    A field that (de)serializes to a :class:`datetime.time` object.

    :param format: Either "time" or "datetime" for serialization to display
        time in either 24 hour or 12 hour+minute+second format.
    :param input_formats: Optional list of formats to also be accepted.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """
    default_error_messages = {
        'invalid': 'Not a valid time.',
    }
    datetime_parser = datetime.datetime.strptime

    def __init__(self, format=NO_DEFAULT,input_formats=None, **kwargs):
        if format is NO_DEFAULT:
            self.format = api_settings.DATETIME_FORMAT
        else:
            self.format = format
        if input_formats is None:
            self.input_formats = api_settings.TIME_INPUT_FORMATS
        else:
            self.input_formats = input_formats

        super().__init__(**kwargs)


    cpdef inline serialize(self, value,dict context):
        if value in (None, ''):
            return None


        if self.format is None or isinstance(value, str):
            return value

        assert not isinstance(value, datetime.datetime), (
            'Expected a `time`, but got a `datetime`. Refusing to coerce, '
            'as this may mean losing timezone information. Use a custom '
            'read-only field and deal with timezone issues explicitly.'
        )

        if self.format.lower() == ISO_8601:
            return value.isoformat()
        return value.strftime(self.format)



    cpdef inline deserialize(self, data, dict context):

        if isinstance(data, datetime.time):
            return data

        for input_format in self.input_formats:
            if input_format.lower() == ISO_8601:
                try:
                    parsed = parse_time(data)
                except (ValueError, TypeError):
                    pass
                else:
                    if parsed is not None:
                        return parsed
            else:
                try:
                    parsed = self.datetime_parser(data, input_format)
                except (ValueError, TypeError):
                    pass
                else:
                    return parsed.time()

        raise self.raise_if_fail('invalid')



@cython.final
cdef class FileField(Field):
    """
    A file field.    

    :param max_length: The maximum file size.
    :param alow_empty_file: Whether to allow uploading empty files.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """
    default_error_messages = {
        'required': 'No file was submitted.',
        'invalid': 'The submitted data was not a file. Check the encoding type on the form.',
        'no_name': 'No filename could be determined.',
        'empty': 'The submitted file is empty.',
        'max_length': 'Ensure this filename has at most {max_length} characters (it has {length}).',
    }

    def __init__(self,**kwargs):
        self.max_length = kwargs.pop('max_length', None)
        self.allow_empty_file = kwargs.pop('allow_empty_file', False)
        super().__init__(**kwargs)

        
    cpdef inline serialize(self,value,dict context):
        if not value :
            return None
        try:
            request = context.get('request', None)
            return request.build_absolute_uri(value.url)
        except:
            return value.url
        
        
    cpdef inline deserialize(self,value,dict context):
        try:
            file_name = value.name
            file_size = value.size
        except AttributeError:
            raise self.raise_if_fail('invalid')
        if not file_name:
            raise self.raise_if_fail('no_name')
        if not self.allow_empty_file and not file_size:
            raise self.raise_if_fail('empty')
        if self.max_length and len(file_name) > self.max_length:
            raise self.raise_if_fail('max_length',max_length=self.max_length, length=len(file_name))

        return value
    
@cython.final
cdef class ArrayField(Field):
    """
    An Array Field.

    :param child: The field to validate the array elements.
    :param allow_empty: Whether the array can be empty.
    :param max_items: The maximum number of items allowed in the array.
    :param min_items: The minimum number of items required in the array.
    :param exac_items: The exact number of items required in the array.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """

    default_error_messages = {
        'not_a_list': 'Expected a list of items but got type "{input_type}".',
        'empty': 'This list may not be empty.',
        'exact_items': 'Must have {exact_items} items.',

    }
    _initial = []

    def __init__(self,child=None,**kwargs):
        self.child = kwargs.pop('child', copy.deepcopy(child))
        self.allow_empty = kwargs.pop('allow_empty', True)
        self.max_items = kwargs.pop('max_items', None)
        self.min_items = kwargs.pop('min_items', None)
        self.exact_items =  kwargs.pop('exact_items', None)
        super().__init__(**kwargs)
        if self.child is not None:
            self.child.bind(field_name='', root=self)
        if self.max_items is not None:
            self.validators.append(MaxLengthValidator(self.max_items,message=f'Must have no more than {self.max_items} items.'))
        if self.min_items is not None:
            self.validators.append(MinLengthValidator(self.min_items,message=f'Must have at least {self.min_items} items.'))

        if self.exact_items is not None:
            self.min_items = self.exact_items
            self.max_items = self.exact_items

                    
    cpdef inline serialize(self,data ,dict context):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        return [ self.child.serialize(item,context) if item is not None else None for item in data]
    
    cpdef inline deserialize(self,data,dict context):
        """
        List of dicts of native values <- List of dicts of primitive datatypes.
        """
        if isinstance(data, (str, dict)) or not hasattr(data, '__iter__'):
            raise self.raise_if_fail('not_a_list', input_type=type(data).__name__)
        if not self.allow_empty and len(data) == 0:
            raise self.raise_if_fail('empty')
        if (
            self.min_items is not None
            and self.min_items == self.max_items
            and len(data) != self.min_items
        ):
            raise self.raise_if_fail("exact_items",exact_items=self.exact_items)
        return self.run_child_validation(data,context)

    cpdef inline run_child_validation(self,data,dict context):
        cdef list result = []
        cdef dict errors = {}
        cdef int idx = 0
        for item in data :
            try:
                result.append(self.child.run_validation(item,context))
            except ValidationError as e:
                errors[idx] = e.detail
            idx +=1

        if not errors:
            return result
        raise ValidationError(errors)
    
@cython.final
cdef class DictField(Field):
    """A Dict Field.

    :param child: The field to validate the dict values.
    :param allow_empty: Whether the dict can be empty.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """
    default_error_messages = {
        'not_a_dict': 'Expected a dict of items but got type "{input_type}".',
        'empty': 'This dict may not be empty.',
    }
    _initial = {}

    def __init__(self,child=None,**kwargs):
        self.child = kwargs.pop('child', copy.deepcopy(child))
        self.allow_empty = kwargs.pop('allow_empty', True)
        super().__init__(**kwargs)
        if self.child is not None:
            self.child.bind(field_name='', root=self)

    cpdef inline serialize(self, data,dict context):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        return {
            str(key) : self.child.serialize(value,context) if value is not None else None for key,value in data.items()
        }
    
    cpdef inline deserialize(self,data,dict context):
        """
        List of dicts of native values <- List of dicts of primitive datatypes.
        """
        if not isinstance(data,dict):
            raise self.raise_if_fail('not_a_dict', input_type=type(data).__name__)
        if not self.allow_empty and len(data) == 0:
            raise self.raise_if_fail('empty')

        return self.run_child_validation(data,context)

    cpdef inline run_child_validation(self,dict data,dict context):
        cdef dict result = {}
        cdef dict errors = {}
        for key,value in data.items():
            try:
                result[str(key)] = self.child.run_validation(value,context)
            except ValidationError as e:
                errors[key] = e.detail

        if not errors:
            return result
        raise ValidationError(errors)

@cython.final
cdef class JSONField(Field):
    """A JSON Field.

    :param binary: Whether to load/dump JSON as binary data.
    :param encoder: The JSON encoder class to use.
    :param decoder: The JSON decoder class to use.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """
    default_error_messages = {
        'invalid': 'Not a valid JSON.'
    }

    def __init__(self, **kwargs):
        self.binary = kwargs.pop('binary', False)
        self.encoder = kwargs.pop('encoder', None)
        self.decoder = kwargs.pop('decoder', None)
        super().__init__(**kwargs)

    cpdef inline serialize(self,value,dict context):
        if self.binary:
            value = json.dumps(value,cls=self.encoder)
            value = value.encode()
        return value

    cpdef inline deserialize(self,data,dict context):
        try:
            if self.binary:
                if isinstance(data, bytes):
                    data = data.decode()
                return json.loads(data,cls=self.decoder)
            else:
                json.dumps(data,cls=self.encoder)
        except (TypeError, ValueError) as e:
            raise self.raise_if_fail('invalid')
        return data


@cython.final
cdef class RelatedField(Field):
    """A Related Field.

    :param queryset: The queryset to use for getting the instance from the given value.
    """
    default_error_messages = {
        'does_not_exist': 'Invalid pk "{pk_value}" - object does not exist.',
        'incorrect_type': 'Incorrect type. Expected pk value, received {data_type}.',

    }
    def __init__(self,**kwargs):
        self.queryset = kwargs.pop('queryset', None)
        super().__init__(**kwargs)
        
    cpdef inline deserialize(self,data,dict context):
        try:
            if isinstance(data, bool):
                raise TypeError
            data = self.queryset.get(pk=data)
        except ObjectDoesNotExist:
            raise self.raise_if_fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError): 
            raise self.raise_if_fail('incorrect_type', data_type=type(data).__name__)
        return data

    
@cython.final
cdef class ManyRelatedField(Field):
    """
    A field used to represent a to-many relationship.

    :param child_relation: The model field that is the reverse of the relation.
    :param allow_empty: Whether the list can be empty.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """
    default_error_messages = {
        'not_a_list': 'Expected a list of items but got type "{input_type}".',
        'empty': 'This list may not be empty.'
    }
    def __init__(self,**kwargs):
        self.child_relation = kwargs.pop('child_relation', None)
        self.allow_empty = kwargs.pop('allow_empty', True)
        super().__init__(**kwargs)
        
    cpdef inline serialize(self,value,dict context):
        
        value = value.all() if hasattr(value, 'all') else value
        return [
            item.pk for item in value
        ]            

    cpdef inline deserialize(self, data,dict context):
        if isinstance(data, str) or not hasattr(data, '__iter__'):
            raise self.raise_if_fail('not_a_list', input_type=type(data).__name__)
        if not self.allow_empty and len(data) == 0:
            raise self.raise_if_fail('empty')
        return [
            self.child_relation.deserialize(item,context)
            for item in data
        ]
        

@cython.final
cdef class ConstantField(Field):
    """
    A field that always outputs a fixed value.

    :param constant: The value to return.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """
    default_error_messages = {
        'constant': 'Must be "{constant}".',
        'None': 'Must be None.'
    }
    def __init__(self,constant,**kwargs):
        self.constant = constant
        super().__init__(**kwargs)
        assert "allow_null" not in kwargs
            
    cpdef inline deserialize(self,data,dict context):
        if data != self.constant:
            if self.constant is None:
                raise self.raise_if_fail("None")
            raise self.raise_if_fail("constant",constant=self.constant)
        return data
    
    
@cython.final
cdef class RecursiveField(Field):
    """
    A field that recursively validates its data.

    :param many: Whether the field is a collection of items.
    :param context: The context passed to the field's :meth:`run_validation`.
    :param only: A tuple or list of field names to include. 
    :param exclude: A tuple or list of field names to exclude.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """
    def __init__(self,**kwargs):
        self.many = kwargs.pop('many',False)
        self.context = kwargs.pop('context',{})
        self.only = kwargs.pop('only',None)
        self.exclude = kwargs.pop('exclude',None)
        if self.only is not None and self.exclude is not None :
            raise OnlyAndExcludeError('You should use either "only" or "exclude"')
        if self.only is not None and not is_collection(self.only):
            raise StringNotCollectionError('"only" should be a list of strings')
        if self.exclude is not None and not is_collection(self.exclude):
            raise StringNotCollectionError('"exclude" should be a list of strings')
        super().__init__(**kwargs)
        
    cpdef inline serialize(self,value,dict context):
        if self.only :
            serializer = self.root.__class__(value,many=self.many,only=self.only,context=self.context)
        elif self.exclude :
            serializer = self.root.__class__(value,many=self.many,exclude=self.exclude,context=self.context)
        else:
            serializer = self.root.__class__(value,many=self.many,context=self.context)
        return serializer.data


@cython.final
cdef class MethodField(Field):
    """
    A field that calls a method on the serializer instead of simply returning a value.

    :param method_name: The name of the method to call.
    :param kwargs: The same keyword arguments that :class:`Field` receives.
    """
    is_method_field = True

    def __init__(self,method_name=None,**kwargs):
        kwargs['read_only']= True
        kwargs['required'] = False
        self.method_name = method_name
        super().__init__(**kwargs)
        
    cpdef inline method_getter(self,field_name, root) :
        if self.method_name is None:
            self.method_name = 'get_{0}'.format(field_name)
        return getattr(root, self.method_name)