from drf_turbo.utils import get_execption_detail

cdef class DrfTurboException(Exception):
    """Base class for all fast_rest-related errors."""
    status_code = 500
    default_detail = 'A server error occurred.'
    default_code = 'error'
    
    def __cinit__(self, detail=None, code=None) -> None:
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
        
        self.detail = get_execption_detail(detail)
        
    def __str__(self) -> str:
        return str(self.detail)

cdef class ValidationError(DrfTurboException):
    default_detail = 'Invalid input.'
    default_code = 'invalid'

    def __cinit__(self, detail=None, code=None) -> None:
        if detail is None:
            detail = self.default_detail
        if code is None:
            code = self.default_code
            
        if isinstance(detail, tuple):
            detail = list(detail)
        elif not isinstance(detail, dict) and not isinstance(detail, list):
            detail = [detail]

        self.detail = get_execption_detail(detail)
        
class StringNotCollectionError(DrfTurboException,TypeError):
    pass


class OnlyAndExcludeError(DrfTurboException):
    pass

            
class ParseError(DrfTurboException):
    status_code = 400
    default_detail = 'Malformed request.'
    default_code = 'parse_error'
