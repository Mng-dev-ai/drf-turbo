cdef object NO_DEFAULT

cdef class SkipField(Exception):
    pass

cdef class Field :
    cdef public :
        str attr
        bint call
        bint required
        bint write_only
        bint read_only
        bint allow_null
        str label
        object default_value
        object initial
        str help_text
        dict style
        str field_name
        object root
        object validators
        dict error_messages
        list attrs

    cpdef serialize(self, value , dict context) 
    cpdef deserialize(self,data, dict context)
    cpdef method_getter(self,field_name, root)
    cpdef void bind(self,basestring name, object root)
    cpdef run_validation(self,object data,dict context)
    cpdef get_initial(self)
    cpdef get_attribute(self, instance,attr=*)
    cpdef get_default_value(self)
    cpdef validate_empty_values(self, data)
    cpdef long validate_or_raise(self,value) except -1


cdef class StrField(Field):
    cdef public:
        allow_blank
        trim_whitespace
        max_length
        min_length

cdef class EmailField(StrField):
    cdef public:
        bint to_lower

cdef class URLField(StrField):
    pass

cdef class RegexField(StrField):
    pass

cdef class IPField(StrField):
    pass

cdef class PasswordField(StrField):
    pass

cdef class UUIDField(StrField):
    pass

cdef class SlugField(Field):
    cdef public:
        allow_unicode
        
cdef class IntField(Field):
    cdef public :
        max_value
        min_value

cdef class FloatField(Field):
    cdef public :
        max_value
        min_value

cdef class DecimalField(Field):
    cdef public:
        max_digits
        decimal_places
        max_value
        min_value
        rounding
        coerce_to_string
        max_whole_digits
    
    cdef validate_precision(self,value)
    cdef quantize(self,value)

cdef class BoolField(Field):
    pass

cdef class ChoiceField(Field):
    cdef public :
        choices
        choice_strings_to_values
        choice_strings_to_display
        allow_blank

cdef class MultipleChoiceField(ChoiceField):
        cdef public:
            allow_empty
            
cdef class DateTimeField(Field):
    cdef public:
        format
        input_formats
        default_timezone
        timezone

    cpdef get_default_timezone(self)
    cpdef enforce_timezone(self, value)

cdef class DateField(Field):
    cdef public:
        format
        input_formats

cdef class TimeField(Field):
    cdef public:
        format
        input_formats

cdef class FileField(Field):
    cdef public :
        max_length
        allow_empty_file

cdef class ArrayField(Field):
    cdef public :
        child
        allow_empty
        min_items
        max_items
        exact_items

    cpdef run_child_validation(self,data,dict context)

cdef class DictField(Field):
    cdef public :
        child
        allow_empty

    cpdef run_child_validation(self,dict data,dict context)


cdef class JSONField(Field):
    cdef public :
        binary
        encoder
        decoder
        

cdef class RelatedField(Field):
    cdef public:
        queryset

cdef class ManyRelatedField(Field):
    cdef public :
        child_relation
        allow_empty

cdef class ConstantField(Field):
    cdef public :
        constant

cdef class RecursiveField(Field):
    cdef public :
        many
        context
        only
        exclude
    cpdef serialize(self,value,dict context)

cdef class MethodField(Field):
    cdef public :
        method_name

