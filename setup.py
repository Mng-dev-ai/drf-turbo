#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup, Extension

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

with open("requirements.txt") as requirements_file:
    requirements = requirements_file.read().splitlines()


setup(
    author="Michael Gendy",
    author_email="nagymichel13@gmail.com",
    python_requires=">=3.8, <3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    description="An alternative serializer implementation for REST framework written in cython built for speed.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="drf_turbo",
    name="drf-turbo",
    packages=find_packages(include=["drf_turbo", "drf_turbo.*"]),
    test_suite="tests",
    url="https://github.com/Mng-dev-ai/drf-turbo",
    version="0.1.8",
    zip_safe=False,
    ext_modules=[
        Extension(
            "drf_turbo.serializer",
            ["drf_turbo/serializer.c"],
        ),
        Extension(
            "drf_turbo.utils",
            ["drf_turbo/utils.c"],
        ),
        Extension(
            "drf_turbo.fields",
            ["drf_turbo/fields.c"],
        ),
        Extension(
            "drf_turbo.exceptions",
            ["drf_turbo/exceptions.c"],
        ),
        Extension(
            "drf_turbo.cython_metaclass",
            ["drf_turbo/cython_metaclass.c"],
        ),
    ]
)
