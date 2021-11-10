from drf_turbo.fields cimport Field
cimport cython_metaclass


cdef class BaseSerializer(Field) :
    cdef:
        object instance
        public bint many
        object data
        public dict context
        readonly object only
        readonly object exclude
        public bint partial 

    cpdef bint is_valid(self,bint raise_exception=*) except -1
    cpdef dict get_initial_data(self)




cdef class Serializer(BaseSerializer):
    cdef inline dict _parse_nested_fields(self,object fields)
    cdef inline void _select_nested_fields(self,Serializer serializer,object fields,basestring action,bint is_nested=*)
    cdef inline object _fields_to_include(self,Serializer serializer,object fields)
    cdef inline object _fields_to_exclude(self,Serializer serializer,object fields,bint is_nested)
    cdef dict _serialize(self,object instance,dict fields)
    cpdef serialize(self,instance,dict context)
    cdef dict _deserialize(self, object data,dict fields)
    cpdef deserialize(self,object data,dict context)
    cpdef run_validation(self,object data,dict context)
    cpdef validate(self,object data)
