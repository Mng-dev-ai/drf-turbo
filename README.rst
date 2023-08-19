=========
drf-turbo
=========


.. image:: https://img.shields.io/pypi/v/drf-turbo.svg
        :target: https://pypi.python.org/pypi/drf-turbo
        :alt: Version

.. image:: https://readthedocs.org/projects/drf-turbo/badge/?version=latest
        :target: https://drf-turbo.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status

.. image:: https://static.pepy.tech/personalized-badge/drf-turbo?period=total&units=international_system&left_color=black&right_color=green&left_text=Downloads
        :target: https://pepy.tech/project/drf-turbo/
        :alt: Downloads


Overview
------------
drf-turbo is a drop-in serializer for Django REST Framework (DRF). drf-turbo serializers run around 7.75 times faster
than what what you get from DRF's packaged serializer.


Requirements
------------

* Django

* Django REST Framework

* pytz

* forbiddenfruit

* pyyaml(OpenAPI)

* uritemplate(OpenAPI)

* djangorestframework-simplejwt(OpenAPI)


Installation
------------

.. code-block:: console

    $ pip install drf-turbo

To install Cython on MacOS `via Brew <https://formulae.brew.sh/formula/cython>`_:

.. code-block:: console

    $ brew install cython

Performance
-----------
`drf-turbo` serialization, deserialization and validation performance averages 86% faster than DRF's standard serializer.

For more details, visit the `benchmarks section <https://drf-turbo.readthedocs.io/en/latest/performance.html>`_ of the docs.

Documentation & Support
-----------------------
Documentation for the project is available at https://drf-turbo.readthedocs.io.

For questions and support, use github issues

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
    # {'username': 'new_test', 'email': 'test2@example.com', 'created': datetime.datetime(2021, 11, 12, 6, 10, 44, 85118)}}

Validation
----------

.. code-block:: python

    serializer = UserSerializer(data={'email': 'test'})
    serializer.is_valid()
    # False
    serializer.errors
    # {'username': ['This field is required.'], 'email': ['Enter a valid email address.'],'created': ['This field is required.']}


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
            self.age = age
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

    serializer = UserSerializer(user,only=('id','username'))

    or

    serializer = ProfileSerializer(profile,exclude=('id','user__email'))

    or

    http://127.0.0.1:8000/user/?only=id,username


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

License
------------
* Free software: MIT license
