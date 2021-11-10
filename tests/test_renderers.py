import pytest
from django.test import TestCase
import drf_turbo as dt


class JSONRendererTests(TestCase):
    """
    Tests specific to the JSON Renderer
    """

    def test_render_lazy_strings(self):
        """
        JSONRenderer should deal with lazy translated strings.
        """
        ret = dt.JSONRenderer().render('test')
        self.assertEqual(ret, b'"test"')

    def test_render_none(self):
        """
        Renderer should deal with None as ''.
        """
        ret = dt.JSONRenderer().render(None)
        self.assertEqual(ret, b'')
        
    def test_render_dict(self):
        """
        Test render dict
        """
        ret = dt.JSONRenderer().render({'a': 'b'})
        self.assertEqual(ret, b'{"a":"b"}')
        
        
    def test_render_list(self):
        """
        Test render list
        """
        ret = dt.JSONRenderer().render(['a', 'b'])
        self.assertEqual(ret, b'["a","b"]')
        
        
    def test_render_int(self):
        """
        Test render int
        """
        ret = dt.JSONRenderer().render(1)
        self.assertEqual(ret, b'1')
        
        
    def test_render_float(self):
        """
        Test render float
        """
        ret = dt.JSONRenderer().render(1.1)
        self.assertEqual(ret, b'1.1')
        
    def test_render_bool(self):
        """
        Test render bool
        """
        ret = dt.JSONRenderer().render(True)
        self.assertEqual(ret, b'true')
                
class ORJSONRendererTests(TestCase):
    """
    Tests specific to the JSON Renderer
    """

    def test_render_lazy_strings(self):
        """
        ORJSONRenderer should deal with lazy translated strings.
        """
        ret = dt.ORJSONRenderer().render('test')
        self.assertEqual(ret, b'"test"')

    def test_render_none(self):
        """
        Renderer should deal with None as ''.
        """
        ret = dt.ORJSONRenderer().render(None)
        self.assertEqual(ret, b'')
        
    def test_render_dict(self):
        """
        Test render dict
        """
        ret = dt.ORJSONRenderer().render({'a': 'b'})
        self.assertEqual(ret, b'{"a":"b"}')
        
        
    def test_render_list(self):
        """
        Test render list
        """
        ret = dt.ORJSONRenderer().render(['a', 'b'])
        self.assertEqual(ret, b'["a","b"]')
        
        
    def test_render_int(self):
        """
        Test render int
        """
        ret = dt.ORJSONRenderer().render(1)
        self.assertEqual(ret, b'1')
        
        
    def test_render_float(self):
        """
        Test render float
        """
        ret = dt.ORJSONRenderer().render(1.1)
        self.assertEqual(ret, b'1.1')
        
    def test_render_bool(self):
        """
        Test render bool
        """
        ret = dt.ORJSONRenderer().render(True)
        self.assertEqual(ret, b'true')
                
class UJSONRendererTests(TestCase):
    """
    Tests specific to the UJSON Renderer
    """

    def test_render_lazy_strings(self):
        """
        UJSONRenderer should deal with lazy translated strings.
        """
        ret = dt.UJSONRenderer().render('test')
        self.assertEqual(ret, b'"test"')

    def test_render_none(self):
        """
        Renderer should deal with None as ''.
        """
        ret = dt.UJSONRenderer().render(None)
        self.assertEqual(ret, b'')
        
    def test_render_dict(self):
        """
        Test render dict
        """
        ret = dt.UJSONRenderer().render({'a': 'b'})
        self.assertEqual(ret, b'{"a":"b"}')
        
        
    def test_render_list(self):
        """
        Test render list
        """
        ret = dt.UJSONRenderer().render(['a', 'b'])
        self.assertEqual(ret, b'["a","b"]')
        
        
    def test_render_int(self):
        """
        Test render int
        """
        ret = dt.UJSONRenderer().render(1)
        self.assertEqual(ret, b'1')
        
        
    def test_render_float(self):
        """
        Test render float
        """
        ret = dt.UJSONRenderer().render(1.1)
        self.assertEqual(ret, b'1.1')
        
    def test_render_bool(self):
        """
        Test render bool
        """
        ret = dt.UJSONRenderer().render(True)
        self.assertEqual(ret, b'true')
        
        


        