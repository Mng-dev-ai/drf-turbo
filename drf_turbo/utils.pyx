#cython: language_level=3, boundscheck=False, wraparound=False, initializedcheck=False, cdivision=True

import collections
from django.utils.encoding import force_str
from django.core.exceptions import ObjectDoesNotExist
import operator


cpdef bint is_iterable_and_not_string(arg):
    return (
        isinstance(arg, collections.Iterable) 
        and not isinstance(arg, str)
    )
    
cpdef bint is_collection(obj):
    """Return True if ``obj`` is a collection type, e.g list, tuple, queryset."""
    return is_iterable_and_not_string(obj) and not isinstance(obj, dict)


cpdef get_error_detail(exc_info):
    """
    Translate django ValidationError to readable errors 
    """
    cdef dict error_dict
    cdef list errors
    cdef str k

    try:
        error_dict = exc_info.error_dict
    except AttributeError:
        return [
            (error.message % error.params) if error.params else error.message
            for error in exc_info.error_list]
    return {
        k: [
            (error.message % error.params) if error.params else error.message
            for error in errors
        ] for k, errors in error_dict.items()
    }


cpdef get_execption_detail(exception):
    if isinstance(exception,(list,tuple)):
        return [get_execption_detail(item) for item in exception]
    
    elif isinstance(exception,dict):
        return {key : get_execption_detail(value) for key,value in exception.items()}

    return force_str(exception)


cpdef get_attribute(instance, attrs):
    for attr in attrs :
        try:
            if isinstance(instance, dict):
                instance = instance[attr]
            else:
                instance = getattr(instance, attr)
        except ObjectDoesNotExist :
            return None

        if callable(instance):
            try:
                instance = instance()
            except (AttributeError, KeyError) as exc:
                raise ValueError(
                    "Unable to resolve attribute '%s' on %s: %s" % (
                        attr, instance, exc
                    )
                )
    return instance

    
cpdef deepcopy(dict data):
    cdef dict output = data.copy()
    cdef str key
    for key, value in output.items():
        output[key] = deepcopy(value) if isinstance(value, dict) else value        
    return output

