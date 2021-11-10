import pytest
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from drf_turbo.exceptions import ParseError
import drf_turbo as dt

class TestJSONParser(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
    
    def test_json_parser(self):
        request = self.factory.post('/', '{"a": "b"}', content_type='application/json')
        assert dt.JSONParser().parse(request) == {'a': 'b'}
        
    def test_json_parser_with_empty_request(self):
        request = self.factory.post('/', '', content_type='application/json')
        with pytest.raises(ParseError):
            dt.JSONParser().parse(request)
        
    def test_json_parser_with_invalid_json(self):   
        request = self.factory.post('/', '{"a": "b"', content_type='application/json')
        with pytest.raises(ParseError):
            dt.JSONParser().parse(request)
                        
            

class TestORJSONParser(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
    
    def test_orjson_parser(self):
        request = self.factory.post('/', '{"a": "b"}', content_type='application/json')
        assert dt.ORJSONParser().parse(request) == {'a': 'b'}
        
    def test_orjson_parser_with_empty_request(self):
        request = self.factory.post('/', '', content_type='application/json')
        with pytest.raises(ParseError):
            dt.ORJSONParser().parse(request)
        
    def test_orjson_parser_with_invalid_json(self):   
        request = self.factory.post('/', '{"a": "b"', content_type='application/json')
        with pytest.raises(ParseError):
            dt.ORJSONParser().parse(request)



class TestUJSONParser(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
    
    def test_ujson_parser(self):
        request = self.factory.post('/', '{"a": "b"}', content_type='application/json')
        assert dt.UJSONParser().parse(request) == {'a': 'b'}
        
    def test_ujson_parser_with_empty_request(self):
        request = self.factory.post('/', '', content_type='application/json')
        with pytest.raises(ParseError):
            dt.UJSONParser().parse(request)
        
    def test_ujson_parser_with_invalid_json(self):   
        request = self.factory.post('/', '{"a": "b"', content_type='application/json')
        with pytest.raises(ParseError):
            dt.UJSONParser().parse(request)

