from django.conf import settings
from drf_turbo.exceptions import ParseError
import json
import codecs


try:
    import ujson
except ImportError:  
    ujson = None  

try:
    import orjson
except ImportError:
    orjson = None  

cimport cython

cdef class BaseParser:
    """
    All parsers should extend `BaseParser`, specifying a `media_type`
    attribute, and overriding the `.parse()` method.
    """
    media_type = None

    cpdef dict parse(self, stream, media_type=None, parser_context=None):
        """
        Given a stream to read from, return the parsed representation.
        Should return parsed data, or a `DataAndFiles` object consisting of the
        parsed data and files.
        """
        raise NotImplementedError(".parse() must be overridden.")


@cython.final
cdef class JSONParser(BaseParser):
    """
    Parses JSON-serialized data.
    """
    media_type = 'application/json'

    cpdef inline dict parse(self, stream, media_type=None, parser_context=None):
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)

        try:
            data = stream.read().decode(encoding)
            return ujson.loads(data)
        except ValueError as exc:
            raise ParseError('JSON parse error - %s' % str(exc))


@cython.final
cdef class UJSONParser(BaseParser):
    """
    Parses JSON-serialized data by ujson parser.
    """

    media_type = "application/json"

    cpdef inline dict parse(self, stream, media_type=None, parser_context=None) :
        assert ujson is not None, "ujson must be installed to use UJSONParser"
        parser_context = parser_context or {}
        encoding = parser_context.get("encoding", settings.DEFAULT_CHARSET)

        try:
            data = stream.read().decode(encoding)
            return ujson.loads(data)
        except ValueError as exc:
            raise ParseError('ORJSON parse error - %s' % str(exc))


@cython.final
cdef class ORJSONParser(BaseParser):
    """
    Parses JSON-serialized data by orjson parser.
    """

    media_type = "application/json"

    cpdef inline dict parse(self, stream, media_type=None, parser_context=None) :
        assert orjson is not None, "orjson must be installed to use ORJSONParser"
        parser_context = parser_context or {}
        encoding = parser_context.get("encoding", settings.DEFAULT_CHARSET)

        try:
            data = stream.read().decode(encoding)
            return orjson.loads(data)
        except ValueError as exc:
            raise ParseError('ORJSON parse error - %s' % str(exc))

