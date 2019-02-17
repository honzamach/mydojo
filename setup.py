#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Author: Honza Mach <honza.mach.ml@gmail.com>
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

#import sys
import os

# To use a consistent encoding
from codecs import open
# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# TODO: This solution has some issues when installing the project in editable mode
# for the first time.
#sys.path.insert(0, os.path.abspath('lib'))
#import mydojo

#-------------------------------------------------------------------------------

def read_file(file_name):
    """Read file and return its contents."""
    with open(file_name, 'r') as fhd:
        return fhd.read()

def read_requirements(file_name):
    """Read requirements file as a list."""
    reqs = read_file(file_name).splitlines()
    if not reqs:
        raise RuntimeError(
            "Unable to read requirements from the {} file.".format(
                file_name
            )
        )
    reqs = [req.split(' ')[0] for req in reqs]
    return reqs

#-------------------------------------------------------------------------------

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name = 'mydojo',
    # TODO: This solution has some issues when installing the project in editable mode
    # for the first time.
    #version = mydojo.__version__,
    version = '0.4.0',
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
    install_requires = read_requirements('etc/requirements.pip'),
    # Add development requirements as extras. This way it is possible to install
    # the package for development locally with following command:
    #
    #   pip install -e .[dev]
    #
    # Resources:
    #   https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-extras-optional-features-with-their-own-dependencies
    #   https://stackoverflow.com/a/28842733
    extras_require = {
        'dev': read_requirements('etc/requirements-dev.pip'),
    },
    scripts = [
        'bin/mydojo-init.sh',
        'bin/mydojo.wsgi'
    ],
    # Add entry point to custom command line interface.
    #
    # Resources:
    #   http://flask.pocoo.org/docs/1.0/cli/#custom-commands
    entry_points={
        'console_scripts': [
            'mydojo-cli=mydojo:cli'
        ],
    },
    include_package_data = True,
    zip_safe = False
)
