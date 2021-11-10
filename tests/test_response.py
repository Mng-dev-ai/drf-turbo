from django.test import TestCase
import drf_turbo as dt


class TestJsonResponse(TestCase):
    def test_json_response(self):
        """
        Test json response
        """
        resp = dt.JSONResponse({'a': 'b'})
        self.assertEqual(resp.content, b'{"a":"b"}')
        
    def test_json_response_with_status(self):
        """
        Test json response with status
        """
        resp = dt.JSONResponse({'a': 'b'}, status=400)
        self.assertEqual(resp.status_code, 400)
        
        
    def test_json_response_with_content_type(self):
        """
        Test json response with content type
        """
        resp = dt.JSONResponse({'a': 'b'}, content_type='application/json')
        self.assertEqual(resp['Content-Type'], 'application/json')
        
        
    def test_json_response_with_content_type_with_charset(self):
        """
        Test json response with content type with charset
        """
        resp = dt.JSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8')
        
        
    def test_json_response_with_content_type_with_charset_and_encoding(self):
        """
        Test json response with content type with charset and encoding
        """
        resp = dt.JSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8')
        
        
    def test_json_response_with_content_type_with_charset_and_encoding_and_encoding_errors(self):
        """
        Test json response with content type with charset and encoding and encoding errors
        """
        resp = dt.JSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore')
        
        
    def test_json_response_with_content_type_with_charset_and_encoding_and_encoding_errors_and_charset_errors(self):
        """
        Test json response with content type with charset and encoding and encoding errors and charset errors
        """
        resp = dt.JSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore')
        
        
    def test_json_response_with_content_type_with_charset_and_encoding_and_encoding_errors_and_charset_errors_and_indent(self):
        """
        Test json response with content type with charset and encoding and encoding errors and charset errors and indent
        """
        resp = dt.JSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4')
        
        
    def test_json_response_with_content_type_with_charset_and_encoding_and_encoding_errors_and_charset_errors_and_indent_and_separators(self):
        """
        Test json response with content type with charset and encoding and encoding errors and charset errors and indent and separators
        """
        resp = dt.JSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4; separators=(, :)')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4; separators=(, :)')
        
        
    def test_json_response_with_content_type_with_charset_and_encoding_and_encoding_errors_and_charset_errors_and_indent_and_separators_and_sort_keys(self):
        """
        Test json response with content type with charset and encoding and encoding errors and charset errors and indent and separators and sort keys
        """
        resp = dt.JSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4; separators=(, :); sort-keys=true')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4; separators=(, :); sort-keys=true')
        
        

class TestORJSONResponse(TestCase):
    def test_orjson_response(self):
        """
        Test orjson response
        """
        resp = dt.ORJSONResponse({'a': 'b'})
        self.assertEqual(resp.content, b'{"a":"b"}')
        
    def test_orjson_response_with_status(self):
        """
        Test orjson response with status
        """
        resp = dt.ORJSONResponse({'a': 'b'}, status=400)
        self.assertEqual(resp.status_code, 400)
        
        
    def test_orjson_response_with_content_type(self):
        """
        Test orjson response with content type
        """
        resp = dt.ORJSONResponse({'a': 'b'}, content_type='application/json')
        self.assertEqual(resp['Content-Type'], 'application/json')
        
        
    def test_orjson_response_with_content_type_with_charset(self):
        """
        Test orjson response with content type with charset
        """
        resp = dt.ORJSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8')
        
    def test_orjson_response_with_content_type_with_charset_and_encoding(self):
        """
        Test orjson response with content type with charset and encoding
        """
        resp = dt.ORJSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8')
        
        
    def test_orjson_response_with_content_type_with_charset_and_encoding_and_encoding_errors(self):
        """
        Test orjson response with content type with charset and encoding and encoding errors
        """
        resp = dt.ORJSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore')
        
    def test_orjson_response_with_content_type_with_charset_and_encoding_and_encoding_errors_and_charset_errors(self):
        """
        Test orjson response with content type with charset and encoding and encoding errors and charset errors
        """
        resp = dt.ORJSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore')
        
        
    def test_orjson_response_with_content_type_with_charset_and_encoding_and_encoding_errors_and_charset_errors_and_indent(self):
        """
        Test orjson response with content type with charset and encoding and encoding errors and charset errors and indent
        """
        resp = dt.ORJSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4')
        
        
    def test_orjson_response_with_content_type_with_charset_and_encoding_and_encoding_errors_and_charset_errors_and_indent_and_separators(self):
        """
        Test orjson response with content type with charset and encoding and encoding errors and charset errors and indent and separators
        """
        resp = dt.ORJSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4; separators=(, :)')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4; separators=(, :)')
        
        
    def test_orjson_response_with_content_type_with_charset_and_encoding_and_encoding_errors_and_charset_errors_and_indent_and_separators_and_sort_keys(self):
        resp = dt.ORJSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4; separators=(, :); sort-keys=true') 
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4; separators=(, :); sort-keys=true')
        
        
class TestUJSONResponse(TestCase):
    def test_ujson_response(self):
        """
        Test ujson response
        """
        resp = dt.UJSONResponse({'a': 'b'})
        self.assertEqual(resp.content, b'{"a":"b"}')
        
    def test_ujson_response_with_status(self):
        """
        Test ujson response with status
        """
        resp = dt.UJSONResponse({'a': 'b'}, status=400)
        self.assertEqual(resp.status_code, 400)
        
        
    def test_ujson_response_with_content_type(self):
        """
        Test ujson response with content type
        """
        resp = dt.UJSONResponse({'a': 'b'}, content_type='application/json')
        self.assertEqual(resp['Content-Type'], 'application/json')
        
        
    def test_ujson_response_with_content_type_with_charset(self):
        """
        Test ujson response with content type with charset
        """
        resp = dt.UJSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8')
        
    def test_ujson_response_with_content_type_with_charset_and_encoding(self):
        """
        Test ujson response with content type with charset and encoding
        """
        resp = dt.UJSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8')
        
        
    def test_ujson_response_with_content_type_with_charset_and_encoding_and_encoding_errors(self):
        """
        Test ujson response with content type with charset and encoding and encoding errors
        """
        resp = dt.UJSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore')
        
    def test_ujson_response_with_content_type_with_charset_and_encoding_and_encoding_errors_and_charset_errors(self):
        """
        Test ujson response with content type with charset and encoding and encoding errors and charset errors
        """
        resp = dt.UJSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore')
        
    def test_ujson_response_with_content_type_with_charset_and_encoding_and_encoding_errors_and_charset_errors_and_indent(self):
        """
        Test ujson response with content type with charset and encoding and encoding errors and charset errors and indent
        """
        resp = dt.UJSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4')
        
        
    def test_ujson_response_with_content_type_with_charset_and_encoding_and_encoding_errors_and_charset_errors_and_indent_and_separators(self):
        """
        Test ujson response with content type with charset and encoding and encoding errors and charset errors and indent and separators
        """
        resp = dt.UJSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4; separators=(, :)')
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4; separators=(, :)')
        
    def test_ujson_response_with_content_type_with_charset_and_encoding_and_encoding_errors_and_charset_errors_and_indent_and_separators_and_sort_keys(self):
        resp = dt.UJSONResponse({'a': 'b'}, content_type='application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4; separators=(, :); sort-keys=true') 
        self.assertEqual(resp['Content-Type'], 'application/json; charset=UTF-8; encoding=UTF-8; encoding-errors=ignore; charset-errors=ignore; indent=4; separators=(, :); sort-keys=true')
        
        
class TestSuccessResponse(TestCase):
    def test_success_response(self):
        """
        Test success response
        """
        resp = dt.SuccessResponse({'a': 'b'})   
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content, b'{"message":"Success","data":{"a":"b"},"error":false}')
        
        
class TestErrorResponse(TestCase):
    def test_error_response(self):
        """
        Test error response
        """
        resp = dt.ErrorResponse({'a': 'b'})
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.content, b'{"message":"Bad request","data":{"a":"b"},"error":true}')
