from django.http import HttpResponse 
from typing import Optional,Any
from rest_framework import status
from django.core.serializers.json import DjangoJSONEncoder
import json

try:
    import ujson
except ImportError:  
    ujson = None  

try:
    import orjson
except ImportError:
    orjson = None  

class JSONResponse(HttpResponse):
    def __init__(self, data : Any,**kwargs) -> None:
        kwargs.setdefault('content_type', 'application/json')
        data = json.dumps(
            data,
            cls=DjangoJSONEncoder,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")
        super().__init__(content=data, **kwargs)
        

class UJSONResponse(HttpResponse):
    def __init__(self, data : Any,**kwargs) -> None:
        assert ujson is not None, "ujson must be installed to use UJSONResponse"
        kwargs.setdefault('content_type', 'application/json')
        data = ujson.dumps(data, ensure_ascii=False).encode("utf-8")
        super().__init__(content=data, **kwargs)


class ORJSONResponse(HttpResponse):
    def __init__(self, data : Any,**kwargs) -> None:
        assert orjson is not None, "orjson must be installed to use ORJSONResponse"
        kwargs.setdefault('content_type', 'application/json')
        data = orjson.dumps(data)
        super().__init__(content=data, **kwargs)


class SuccessResponse :
    
    def __new__(cls,data,message:Optional[str]=None,status_code:Optional[int]=None,default:Any=JSONResponse) -> Any :
        if not message : 
            message = 'Success'
        if not status_code :
            status_code = status.HTTP_200_OK
        return default(dict([
            ('message', message),
            ('data', data),
            ('error' , False)
    ]),status=status_code)



class ErrorResponse : 

    def __new__(cls,data,message:Optional[str]=None,status_code:Optional[int]=None,default: Any=JSONResponse) -> Any :
        if not message : 
            message = 'Bad request'
        if not status_code :
            status_code = status.HTTP_400_BAD_REQUEST
        return default(dict([
            ('message', message),
            ('data', data),
            ('error' , True )
    ]),status=status_code)