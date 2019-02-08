#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
MyDojo - My personal internet Dojo
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"
__version__ = "0.1.0"


import click
from flask.cli import FlaskGroup


# Expose main application factory to current namespace
from .app import create_app


@click.group(cls = FlaskGroup, create_app = create_app)
def cli():
    """Command line interface for the MyDojo application."""
