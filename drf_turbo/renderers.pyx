from django.http.multipartparser import parse_header
from rest_framework.utils import encoders, json
from rest_framework.compat import (
    INDENT_SEPARATORS, LONG_SEPARATORS, SHORT_SEPARATORS
)   
try:
    import orjson
except ImportError:
    orjson = None  

try:
    import ujson
except ImportError:
    ujson = None  


cimport cython

cdef zero_as_none(value):
    return None if value == 0 else value

cdef class BaseRenderer:
    """
    All renderers should extend this class, setting the `media_type`
    and `format` attributes, and override the `.render()` method.
    """
    media_type = None
    format = None
    charset = 'utf-8'
    render_style = 'text'

    cpdef bytes render(self,data, accepted_media_type=None,renderer_context=None):
        raise NotImplementedError('Renderer class requires .render() to be implemented')


@cython.final
cdef class JSONRenderer(BaseRenderer):
    """
    Renderer which serializes to JSON.
    """
    media_type = 'application/json'
    format = 'json'
    encoder_class = encoders.JSONEncoder
    ensure_ascii = False
    compact = True
    strict = True
    charset = None

    cpdef inline get_indent(self,unicode accepted_media_type, dict renderer_context):
        if accepted_media_type:
            base_media_type, params = parse_header(accepted_media_type.encode('ascii'))
            try:
                return zero_as_none(max(min(int(params['indent']), 8), 0))
            except (KeyError, ValueError, TypeError):
                pass
        return renderer_context.get('indent', None)

    cpdef inline bytes render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into JSON, returning a bytestring.
        """
        cdef basestring ret
        if data is None:
            return b''

        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        if indent is None:
            separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS
        else:
            separators = INDENT_SEPARATORS

        ret = json.dumps(
            data, cls=self.encoder_class,
            indent=indent, ensure_ascii=self.ensure_ascii,
            allow_nan=not self.strict, separators=separators
        )

        ret = ret.replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
        return ret.encode()

@cython.final
cdef class UJSONRenderer(BaseRenderer):
    """
    Renderer which serializes to JSON.
    """
    media_type = 'application/json'
    format = 'json'
    ensure_ascii = False
    escape_forward_slashes= False   
    encode_html_chars= False
    charset = None


    cpdef inline get_indent(self,unicode accepted_media_type, dict renderer_context):
        cdef dict params
        if accepted_media_type:
            _, params = parse_header(accepted_media_type.encode('ascii'))
            try:
                return zero_as_none(max(min(int(params['indent']), 8), 0))
            except (KeyError, ValueError, TypeError):
                pass

        return renderer_context.get('indent', None)

    cpdef inline bytes render(self, data,accepted_media_type=None,renderer_context=None):
        """
        Render `data` into JSON, returning a bytestring.
        """
        assert ujson is not None, "ujson must be installed to use UJSONRenderer"
        cdef basestring ret
        if data is None:
            return b''

        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)


        ret = ujson.dumps(
            data,
            indent=indent or 0, 
            ensure_ascii=self.ensure_ascii,
            encode_html_chars=self.encode_html_chars,
            escape_forward_slashes=self.escape_forward_slashes,
        )
        ret = ret.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
        return bytes(ret.encode("utf-8"))

@cython.final
cdef class ORJSONRenderer(BaseRenderer):
    """
    Renderer which serializes to JSON.
    """

    media_type = "application/json"
    format = "json"
    charset = None
        


    cpdef inline bytes render(self, data,accepted_media_type=None,renderer_context=None):
        """
        Render `data` into JSON, returning a bytestring.
        """
        assert orjson is not None, "orjson must be installed to use ORJSONParser"
        if data is None:
            return b''

        return orjson.dumps(
            data,
            option = orjson.OPT_SERIALIZE_UUID | \
                orjson.OPT_SERIALIZE_NUMPY | \
                orjson.OPT_SERIALIZE_DATACLASS | \
                orjson.OPT_NON_STR_KEYS,
        )
