# cython: language_level=3
# cython: embedsignature=True
# cython: wraparound=False
# cython: nonecheck=False
# cython: boundscheck=False

from django.utils.functional import cached_property
from drf_turbo.fields cimport Field,RelatedField,SkipField,NO_DEFAULT
from drf_turbo.exceptions import *
from drf_turbo.utils import *
from django.core.exceptions import ValidationError as DjangoValidationError
from collections.abc import Mapping
import traceback
cimport cython

cdef class BaseSerializer(Field):
    """
    Base class for all serializers.
    
    :param instance: The instance to be serialized.
    :param many: Serialize single object or a list of objects.
    :param data: The data to be deserialized.
    :param context: The context dictionary passed to the serializer.
    :param partial: If set to True, partial update will be allowed.
    :param only: A list of fields to be included in the serialized data.
    :param exclude: A list of fields to be excluded from the serialized data.
    :param kwargs: Extra keyword arguments.

    """
    def __init__(
        self, 
        object instance = None, 
        bint many = False, 
        object data = None, 
        dict context = None,
        object only = None,
        object exclude = None,
        bint partial = False,
        **kwargs
        ):
        if only is not None and exclude is not None :
            raise OnlyAndExcludeError('You should use either "only" or "exclude"')
        if only is not None and not is_collection(only):
            raise StringNotCollectionError('"only" should be a list of strings')
        if exclude is not None and not is_collection(exclude):
            raise StringNotCollectionError('"exclude" should be a list of strings')
        super().__init__(**kwargs)
        self._instance =instance
        self._data = data
        self.many = many 
        self._initial_data = None
        self._initial_instance = None
        self.context = context
        self.only = only
        self.exclude = exclude
        self.partial = partial
        
   
    cpdef bint is_valid(self,bint raise_exception=False) except -1:
        """
        Whether the data is valid.

        :param raise_exception: Whether to raise an exception if the data is invalid.

        """
        assert hasattr(self, '_data'), (
            'Cannot call `.is_valid()` as no `data=` keyword argument was '
            'passed when instantiating the serializer instance.'
        )
        if not hasattr(self, '_validated_data'):
            try:
                self._validated_data =self.run_validation(self._data,self.context)
            except ValidationError as exc:
                self._validated_data = {}
                self._errors = exc.detail
            else:
                self._errors = {}

        if self._errors and raise_exception:
            raise ValidationError(self.errors)
        return not bool(self._errors)
    
    
    def save(self,**kwargs):
        """
        Create or update a model instance.

        :param kwargs: Extra keyword arguments.
        """
        assert not self._initial_data, (
            "You cannot call `.save()` after accessing `serializer.data`."
            "If you need to access data before committing to the database then "
            "inspect 'serializer.validated_data' instead. "
        )

        validated_data = {**self.validated_data, **kwargs}
        if self._instance is not None:
            self._instance = self.update(self._instance, validated_data)
        else:
            self._instance = self.create(validated_data)

        return self._instance
    

    @property
    def errors(self):
        """
        Return the dictionary of errors raised during validation.
        """
        if not hasattr(self, '_errors'):
            msg = 'You must call `.is_valid()` before accessing `.errors`.'
            raise AssertionError(msg)
        return self._errors
    
    cpdef dict get_initial_data(self):
        """
        Return the initial data for the fields.
        """
        if self._data is not None:

            if not isinstance(self._data, Mapping):
                return dict()
            return dict([
                (name, self._data.get(name,NO_DEFAULT))
                for name, field in self.fields.items()
                if (self._data.get(name,NO_DEFAULT) is not NO_DEFAULT) and
                not field.read_only
            ])

        return dict([
            (name, field.get_initial())
            for name,field in self.fields.items()
            if not field.read_only
        ])

    @property
    def data(self):
        """
        Return the serialized data on the serializer.
        """
        if not self._initial_data :
            if self._instance is not None and not getattr(self, '_errors', None):
                self._initial_data = self.serialize(self._instance,self.context)
            elif hasattr(self, '_validated_data') and not getattr(self, '_errors', None):
                self._initial_data = self.serialize(self.validated_data,self.context)

            else:
                self._initial_data = self.get_initial_data()

        return self._initial_data
    
    @property
    def instance(self):
        """
        Return the model instance that is being serialized.
        """
        return self._instance

    
    @property
    def validated_data(self):
        """
        Return the validated data on the serializer.
        """
        if not hasattr(self, '_validated_data'):
            msg = 'You must call `.is_valid()` before accessing `.validated_data`.'
            raise AssertionError(msg)
        return self._validated_data
    
cdef class Serializer(BaseSerializer):
    
    def __getmetaclass__(_):
        from drf_turbo.meta import SerializerMetaclass
        return SerializerMetaclass

    def get_fields(self):
        """
        Return the dict of field names -> field instances that should be added to the serializer. 
        """
        return deepcopy(self._fields)
    

    def fields(self):
        """
        This is a shortcut for accessing the dict on the *fields* attribute. 
        """
        cdef str key
        cdef Field value
        cdef dict fields = {}
        for key, value in self.get_fields().items():
            fields[key] = value            
            fields[key].bind(key,self)
        return fields
    
    from forbiddenfruit import curse as _curse
    _curse(Serializer,'fields',cached_property(fields))
    Serializer.fields.__set_name__(Serializer, 'fields')


    @property
    def _writable_fields(self):    
        """
        @property _writable_fields
        Return a list of all writable fields.
        """
        cdef str k
        cdef Field v
        return {k: v for k, v in self.fields.items() if not v.read_only}
    

    @property
    def _readable_fields(self):
        """
        Return a list of all readable fields.
        """
        cdef str k
        cdef Field v
        return {k: v for k, v in self.fields.items() if not v.write_only}
    
    @property
    def _only_fields(self):  
        """
        Return a list of all fields that have been specified in the `only` option.
        """
        only = self.only or self.context.get('request').GET.get('only').split(',')
        is_nested = any('__' in field for field in only)
        if is_nested :
            fields = self._parse_nested_fields(only)
            self._select_nested_fields(self,fields,action='include') 
        else:
            self._fields_to_include(self,only)
        return self.fields
    
    @property
    def _exclude_fields(self):
        """
        Return a list of all fields that have been specified in the `exclude` option.
        """
        exclude = self.exclude or self.context.get('request').GET.get('exclude').split(',')
        is_nested = any('__' in field for field in exclude)
        if is_nested:
            fields = self._parse_nested_fields(exclude)
            self._select_nested_fields(self,fields,action='exclude',is_nested=True) 
        else:
            self._fields_to_exclude(self,exclude,is_nested=False)
                        
        return self.fields
    
    cdef inline dict _parse_nested_fields(self,object fields):
        """
        Parse nested fields

        :param fields: A list of fields to parse.
        """
        cdef dict field_object = {"fields": []}
        cdef str f
        for f in fields:
            obj = field_object
            nested_fields = f.split("__")
            for v in nested_fields:
                if v not in obj["fields"]:
                    obj["fields"].append(v)
                if nested_fields.index(v) < len(nested_fields) - 1:
                    obj[v] = obj.get(v, {"fields": []})
                    obj = obj[v]
        return field_object
    
    cdef inline void _select_nested_fields(self,Serializer serializer,object fields,basestring action,bint is_nested=False):
        for k in fields:
            if k == "fields":
                if action == 'include' :
                    self._fields_to_include(serializer, fields[k])
                elif action == 'exclude':
                    self._fields_to_exclude(serializer,fields[k],is_nested)

            else:
                self._select_nested_fields(serializer.fields[k], fields[k],action=action,is_nested=is_nested)
    
    cdef inline object _fields_to_include(self,Serializer serializer,object fields):
        """
        Include fields.

        :param serializer: The serializer to include fields on.
        :param fields: A list of fields to include.
        """
        allowed = set(fields)
        existing = set(serializer.fields.keys())
        for field_name in existing - allowed:
            if field_name in serializer.fields :
                serializer.fields.pop(field_name)
        return serializer.fields
    
    cdef inline object _fields_to_exclude(self,Serializer serializer,object fields,bint is_nested):
        """
        Exclude fields.

        :param serializer: The serializer to exclude fields on.
        :param fields: A list of fields to exclude.
        :param is_nested: Whether the fields are nested.
        """
        excluded = set(fields)
        existing = set(serializer.fields.keys())
        for field_name in excluded :
            if is_nested :
                if field_name in existing :
                    if field_name in self.fields.keys() :
                        if not issubclass(self.fields[field_name].__class__,Serializer):
                            serializer.fields.pop(field_name)
                    else:
                        serializer.fields.pop(field_name)
            else:
                if field_name in serializer.fields:
                    serializer.fields.pop(field_name)
        return serializer.fields


    cdef dict _serialize(self,object instance,dict fields):
        
        cdef str name
        cdef Field field
        cdef dict ret = {}
        cdef bint is_dict
        for name,field in fields.items():
            attr = field.attr if field.attr and not '.' in field.attr else name
            if field.is_method_field:   
                result = field.method_getter(attr,self.__class__)(self,instance)
            else:
                try:
                    if isinstance(field,RelatedField):
                        result = field.get_attribute(instance,attr + '_id')
                    else:
                        result = field.get_attribute(instance)
                        if hasattr(result,'all'):
                            result = result.all()
                                            
                except SkipField :
                    continue
                   
                if result is not None:
                    if field.call:
                        result = result()
                    result = field.serialize(result,self.context)
            ret[attr] = result
            
        return ret    
    
    
    cpdef serialize(self,object instance,dict context):
        """
        Serialize a model instance.

        :param instance: Model instance to serialize.
        :param context: Context data.
        """
        try:
            only = self.context.get('request').GET.get('only')
        except :
            only = None
        try:
            exclude = self.context.get('request').GET.get('exclude')
        except :
            exclude = None
        if self.only or only is not None :
            fields = self._only_fields
        elif self.exclude or exclude is not None:
            fields = self._exclude_fields
        fields = self._readable_fields
        if self.many :
            return [self._serialize(o,fields) for o in instance]
        return self._serialize(instance,fields)
    
    cdef dict _deserialize(self, object data,dict fields):
        if not isinstance(data, Mapping):
            raise ValidationError(
                'Invalid data type: %s' % type(data).__name__
            )
        cdef dict ret = {} 
        cdef dict errors = {}
        cdef str name
        for name,field in fields.items():
            attr = field.attr if field.attr and not '.' in field.attr else name
            validate_method = getattr(self, 'validate_' + attr, None)
            value = data.get(name,NO_DEFAULT)
            try:
                validated_value = field.run_validation(value,self.context)
                if validate_method is not None:
                    validated_value = validate_method(validated_value)

            except ValidationError as exc:
                errors[name] = exc.detail
            except DjangoValidationError as exc:
                errors[name] = get_error_detail(exc)
            except SkipField:
                continue
            else:
                ret[attr] = validated_value
                    
        if errors:
            raise ValidationError(errors)
        return ret

    cpdef deserialize(self,object data,dict context):
        """
        Given a dictionary-like structure, build a dictionary of deserialized
        fields and return a model instance.

        :param data: The data to deserialize.
        :param context: The context for the request.
        """
        fields = self._writable_fields
        if self.many :
            return [self._deserialize(o,fields) for o in data]
        return self._deserialize(data,fields)
    
    cpdef run_validation(self,object data,dict context):
        """
        Validate an entire bundle of data.

        :param data: The data to validate.
        :param context: The context for the request.
        """
        value = self.validate(self.deserialize(data,context))
        return value
    
    cpdef validate(self,object data):
        """
        Validate a dictionary of deserialized field values.

        :param data: A dictionary of deserialized field values.
        """
        return data
    
    
    

cdef class ModelSerializer(Serializer):
    
    def __getmetaclass__(_):
        from drf_turbo.meta import ModelSerializerMetaclass
        return ModelSerializerMetaclass

    cpdef create(self, validated_data):
        """
        Create a model instance.

        :param validated_data: A dictionary of validated data.
        """
        model = self.Meta.model
        opts = model._meta.concrete_model._meta
        many_to_many_fields = [field.name for field in opts.many_to_many if field.serialize]
        m2m_fields = {}
        data = validated_data.copy()
        for attr, value in data.items():
            if attr in many_to_many_fields :
                m2m_fields[attr] = validated_data.pop(attr)
            

        try:
            instance = model._default_manager.create(**validated_data)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                'Got a `TypeError` when calling `%s.%s.create()`. '
                'This may be because you have a writable field on the '
                'serializer class that is not a valid argument to '
                '`%s.%s.create()`. You may need to make the field '
                'read-only, or override the %s.create() method to handle '
                'this correctly.\nOriginal exception was:\n %s' %
                (
                    model.__name__,
                    model._default_manager.name,
                    model.__name__,
                    model._default_manager.name,
                    self.__class__.__name__,
                    tb
                )
            )
            raise TypeError(msg)
        # Save many-to-many relationships after the instance is created.
        if m2m_fields:
            for field_name, value in m2m_fields.items():
                field = getattr(instance, field_name)
                field.set(value)

        return instance


    cpdef update(self, instance, validated_data):
        """
        Update a model instance.

        :param instance: Model instance to update.
        :param validated_data: A dictionary of deserialized data.
        """
        opts = instance._meta.concrete_model._meta
        many_to_many_fields =[field.name for field in opts.many_to_many if field.serialize]
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in many_to_many_fields :
                m2m_fields.append((attr, value))
            else:    
                setattr(instance, attr, value)

        instance.save()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance
