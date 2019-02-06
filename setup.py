#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

"""
Usage
--------------------------------------------------------------------------------

Install package locally for development:

    pip install -e .[dev]

Resources:
--------------------------------------------------------------------------------

* https://packaging.python.org/en/latest/
* https://python-packaging.readthedocs.io/en/latest/index.html
* https://setuptools.readthedocs.io/en/latest/setuptools.html

"""

import sys
import os

# To use a consistent encoding
from codecs import open
# Always prefer setuptools over distutils
from setuptools import setup, find_packages

#
# Import local version of MyDojo library, so that we can insert correct version
# number into package.
#
sys.path.insert(0, os.path.abspath('.'))
import mydojo

here = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------------------------------------------------

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'mydojo',
    version = mydojo.__version__,
    description = 'My personal internet Dojo',
    long_description = long_description,
    classifiers = [
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords = 'library',
    url = 'https://github.com/honzamach/mydojo',
    author = 'Honza Mach',
    author_email = 'honza.mach.ml@gmail.com',
    license = 'MIT',
    packages = find_packages(),
    test_suite = 'nose.collector',
    tests_require = [
        'nose'
    ],
    install_requires=[
        'pytz==2018.5',
        'babel==2.6.0',
        'jinja2==2.10',
        'blinker==1.4',
        'flask==1.0.2',
        'flask-babel==0.11.2',
        'flask-debugtoolbar==0.10.1',
        'flask-jsglue==0.3.1'
    ],
    # Add development requirements as extras. This way it is possible to install
    # the package for development locally with following command:
    #
    #   pip install -e .[dev]
    #
    # Resources:
    #   https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies
    #   https://stackoverflow.com/a/28842733
    extras_require = {
        'dev': [
            'pyflakes',
            'pylint',
            'sphinx',
            'sphinx-rtd-theme'
        ]
    },
    scripts = [
        'bin/mydojo.wsgi',
        'bin/mydojo-dev.py'
    ],
    include_package_data = True,
    zip_safe = False
)
