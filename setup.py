#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
from distutils.extension import Extension
from Cython.Build import cythonize


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().splitlines()


setup(
    author="Michael Gendy",
    author_email='mngback@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="An alternative serializer implementation for REST framework written in cython built for speed.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='drf_turbo',
    name='drf-turbo',
    packages=find_packages(include=['drf_turbo', 'drf_turbo.*']),
    test_suite='tests',
    url='https://github.com/Mng-dev-ai/drf-turbo',
    version='0.1.2',
    zip_safe=False,
    ext_modules=cythonize(["drf_turbo/*.pyx"]),

)
