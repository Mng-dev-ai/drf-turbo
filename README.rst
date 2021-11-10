=========
drf-turbo
=========


.. image:: https://img.shields.io/pypi/v/drf-turbo.svg
        :target: https://pypi.python.org/pypi/drf-turbo

.. image:: https://img.shields.io/travis/Mng-dev-ai/drf-turbo.svg
        :target: https://travis-ci.com/Mng-dev-ai/drf-turbo

.. image:: https://readthedocs.org/projects/drf-turbo/badge/?version=latest
        :target: https://drf-turbo.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/Mng-dev-ai/drf-turbo/shield.svg
     :target: https://pyup.io/repos/github/Mng-dev-ai/drf-turbo/
     :alt: Updates



An alternative serializer implementation for REST framework written in cython built for speed.


* Free software: MIT license
* Documentation: https://drf-turbo.readthedocs.io.


**NOTE**: Cython is required to build this package.


Requirements
------------

* Django

* Django REST Framework

* Cython

* forbiddenfruit

* psycopg2-binary

* pyyaml(OpenAPI)

* uritemplate(OpenAPI)

* djangorestframework-simplejwt(OpenAPI)


Installation
------------

.. code-block:: console

    $ pip install drf-turbo


Examples
========

Declaring Serializers
---------------------
.. code-block:: python

   from datetime import datetime
   from django.utils.timezone import now
   import drf_turbo as dt

    class User:
        def __init__(self, username, email,created=None):
            self.username = username
            self.email = email
            self.created = created or datetime.now()

        user = User(username='test' , email='test@example.com')



    class UserSerializer(dt.Serializer):
        username = dt.StrField(max_length=50)
        email = dt.EmailField()
        created = dt.DateTimeField()


Serializing objects
-------------------

.. code-block:: python


   serializer = UserSerializer(user)
   serializer.data

    # {'username': 'test', 'email': 'test@example.com', 'created': '2021-11-04T22:49:01.981127Z'}


Deserializing objects
---------------------

.. code-block:: python

    data = {'username':'new_test','email':'test2@example.com','created':now()}
    serializer = UserSerializer(data=data)
    serializer.is_valid()
    # True
    serializer.validated_data
    # {'username': 'new_test', 'email': 'test2@example.com', 'created': '2021-11-04T23:29:13.191304Z'}

Validation
----------

.. code-block:: python

    serializer = UserSerializer(data={'email': 'test'})
    serializer.is_valid()
    # False
    serializer.errors
    # {'username': ['This field is required.'], 'email': ['Enter a valid email address.']}


Field-level validation
----------------------

.. code-block:: python

    import drf_turbo as dt

    class UserSerializer(dt.Serializer):
        username = dt.StrField(max_length=50)

        def validate_username(self, value):
            if 'test' not in value.lower():
                raise dt.ValidationError("test must be in username")
            return value

Object-level validation
-----------------------

.. code-block:: python

    import drf_turbo as dt

    class CampaignSerializer(dt.Serializer):
        start_date = dt.DateTimeField()
        end_date = dt.DateTimeField()

        def validate(self, data):
            if data['start_date'] > data['end_date']:
                raise dt.ValidationError("start_date must occur before end_date")
            return data

Nested Serializers
------------------
.. code-block:: python

   from datetime import datetime
   from django.utils.timezone import now
   import drf_turbo as dt

    class User:
        def __init__(self, username, email,created=None):
            self.username = username
            self.email = email
            self.created = created or datetime.now()

        user = User(username='test' , email='test@example.com')

    class UserSerializer(dt.Serializer):
        username = dt.StrField(max_length=50)
        email = dt.EmailField()
        created = dt.DateTimeField()

    class Profile : 
        def __init__(self, age=25):
            self.user = user

        profile = Profile()


    class ProfileSerializer(dt.Serializer):
        age = dt.IntField()
        user = UserSerializer()

    
    serializer = ProfileSerializer(profile)
    serializer.data

    # {'age' : 25 , 'user' : {'username': 'test', 'email': 'test@example.com', 'created': '2021-11-04T22:49:01.981127Z'}}

    
Filtering Output
----------------

drf-turbo provides option to enclude or exclude fields from serializer using ``only`` or ``exclude`` keywords.

.. code-block:: python

    serializer = UserSerializer(only=('id','username'))

    or 

    serializer = ProfileSerializer(exclude=('id','user__email'))

    or 

    http://127.0.0.1:8000/?only=id,username

    
Required Fields
---------------

Make a field required by passing required=True. An error will be raised if the the value is missing from data during Deserializing.

For example:

.. code-block:: python

    class UserSerializer(dt.Serializer):

        username = dt.StrField(required=True,error_messages={"required":"no username"})



Specifying Defaults
-------------------

It will be used for the field if no input value is supplied.


For example:

.. code-block:: python

    from datetime import datetime

    class UserSerializer(dt.Serializer):

        birthdate = dt.DateTimeField(default=datetime(2021, 11, 05))




ModelSerializer
---------------

Mapping serializer to Django model definitions.

Features : 

    * It will automatically generate a set of fields for you, based on the model.
    * It will automatically generate validators for the serializer.
    * It includes simple default implementations of .create() and .update().

.. code-block:: python

    class UserSerializer(dt.ModelSerializer):

        class Meta : 
            model = User
            fields = ('id','username','email')

You can also set the fields attribute to the special value ``__all__``  to indicate that all fields in the model should be used.

For example:

.. code-block:: python

    class UserSerializer(dt.ModelSerializer):

        class Meta : 
            model = User
            fields = '__all__'

You can set the exclude attribute to a list of fields to be excluded from the serializer.

For example:

.. code-block:: python

    class UserSerializer(dt.ModelSerializer):

        class Meta : 
            model = User
            exclude = ('email',)
    

Read&Write only fields
----------------------

.. code-block:: python

    class UserSerializer(dt.ModelSerializer):
        class Meta:
            model = User
            fields = ('id', 'username', 'password','password_confirmation')
            read_only_fields = ('username')
            write_only_fields = ('password','password_confirmation')

Parsers
-------

Allow only requests with JSON content, instead of the default of JSON or form data.

.. code:: python

    REST_FRAMEWORK = {
        'DEFAULT_PARSER_CLASSES': [
            'drf_turbo.parsers.JSONParser',
        ]
    }

    or 

    REST_FRAMEWORK = {
        'DEFAULT_PARSER_CLASSES': [
            'drf_turbo.parsers.UJSONParser',
        ]
    }

    or 

    REST_FRAMEWORK = {
        'DEFAULT_PARSER_CLASSES': [
            'drf_turbo.parsers.ORJSONParser',
        ]
    }

**NOTE**: ujson must be installed to use UJSONParser.   

**NOTE**: orjson must be installed to use ORJSONParser.



Renderers
---------

Use JSON as the main media type.

.. code:: python


    REST_FRAMEWORK = {
        'DEFAULT_RENDERERS_CLASSES': [
            'drf_turbo.renderers.JSONRenderer',
        ]
    }

    or

    REST_FRAMEWORK = {
        'DEFAULT_RENDERERS_CLASSES': [
            'drf_turbo.renderers.UJSONRenderer',
        ]
    }

    or

    REST_FRAMEWORK = {
        'DEFAULT_RENDERERS_CLASSES': [
            'drf_turbo.renderers.ORJSONRenderer',
        ]
    }

**NOTE**: ujson must be installed to use UJSONRenderer.   

**NOTE**: orjson must be installed to use ORJSONRenderer.



Responses
---------

An ``HttpResponse`` subclass that helps to create a JSON-encoded response. Its default Content-Type header is set to application/json.

.. code:: python

    from rest_framework.views import APIView
    import drf_turbo as dt

    class UserInfo(APIView):
        def get(self,request):
            data = {"username":"test"}
            return dt.JsonResponse(data,status=200)

    or 

    class UserInfo(APIView):
        def get(self,request):
            data = {"username":"test"}
            return dt.UJSONResponse(data,status=200)

    or

    class UserInfo(APIView):
        def get(self,request):
            data = {"username":"test"}
            return dt.ORJSONResponse(data,status=200)

**NOTE**: ujson must be installed to use UJSONResponse.   

**NOTE**: orjson must be installed to use ORJSONResponse.

    
Also drf-turbo provides an easy way to return a success or error response using ``SuccessResponse`` or ``ErrorResponse`` clasess.

for example : 

.. code:: python

    class UserInfo(APIView):
        def get(self,request):
            data = {"username":"test"}
            serializer = UserSerializer(data=data)
            if not serializer.is_valid():
                return dt.ErrorResponse(serializer.errors)
                 # returned response :  {'message':'Bad request', data : ``serializer_errros``, 'error': True} with status = 400
            return dt.SuccessResponse(data)     
            # returned response :  {'message':'Success', data : {"username":"test"} , 'error': False} with status = 200





OpenApi(Swagger)
----------------

Add drf-turbo to installed apps in ``settings.py``

.. code:: python

    INSTALLED_APPS = [
        # ALL YOUR APPS
        'drf_turbo',
    ]


and then register our openapi AutoSchema with DRF.

.. code:: python

    REST_FRAMEWORK = {
        # YOUR SETTINGS
        'DEFAULT_SCHEMA_CLASS': 'drf_turbo.openapi.AutoSchema',
    }


and finally add these lines in ``urls.py``

.. code:: python

    from django.views.generic import TemplateView
    from rest_framework.schemas import get_schema_view as schema_view
    from drf_turbo.openapi import SchemaGenerator
    
    urlpatterns = [
        # YOUR PATTERNS
 	path('openapi', schema_view(
            title="Your Project",
            description="API for all things …",
            version="1.0.0",
            generator_class=SchemaGenerator,
            public=True,
        ), name='openapi-schema'),
        path('docs/', TemplateView.as_view(
            template_name='docs.html',
            extra_context={'schema_url':'openapi-schema'}
        ), name='swagger-ui'),
    ]
    
Now go to http://127.0.0.1:8000/docs

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
