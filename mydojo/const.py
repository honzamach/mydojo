#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains global application-wide constants for MyDojo user interface.
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import re


CRE_EMAIL = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
"""Compiled regular expression for email address format validation."""

CRE_COUNTRY_CODE = re.compile("^[a-zA-Z]{2,3}$")
"""Compiled regular expression for validating language/country codes."""


MYDOJO_DEFAULT_LOCALE = 'en'
"""Default application locale."""

MYDOJO_DEFAULT_TIMEZONE = 'UTC'
"""Default application timezone."""


FLASH_INFO = 'info'
"""Class for *info* flash messages."""

FLASH_SUCCESS = 'success'
"""Class for *success* flash messages."""

FLASH_WARNING = 'warning'
"""Class for *warning* flash messages."""

FLASH_FAILURE = 'danger'
"""Class for *failure* flash messages."""


CFGKEY_MODULES_LOADED = 'MYDOJO_MODULES_LOADED'
"""Configuration key name: Registry of all successfully loaded blueprints."""

CFGKEY_MODULES_REQUESTED = 'MYDOJO_MODULES'
"""Configuration key name: List of all requested blueprints."""


RESOURCE_BABEL = 'babel'
"""Name for the ``flask_babel.Babel`` object within the application resources."""


FA_ICONS = {

    #
    # General icons.
    #
    'missing-icon': '<i class="fas fa-fw fa-question" title="Missing icon"></i>',
    'language':     '<i class="fas fa-fw fa-globe"></i>',

    #
    # Main site section icons.
    #
    'section-home':           '<i class="fas fa-fw fa-home"></i>',

    #
    # Built-in module icons.
    #
    'module-design':             '<i class="fas fa-fw fa-palette"></i>',


    #
    # Flash message/alert icons.
    #
    'alert-success': '<i class="fas fa-fw fa-check-circle"></i>',
    'alert-info':    '<i class="fas fa-fw fa-info-circle"></i>',
    'alert-warning': '<i class="fas fa-fw fa-exclamation-circle"></i>',
    'alert-danger':  '<i class="fas fa-fw fa-exclamation-triangle"></i>',

    #
    # Various additional uncategorized icons.
    #
    'ajax-loader': '<i class="fas fa-fw fa-spinner fa-spin fa-4x"></i>',
    'caret-down':  '<i class="fas fa-fw fa-caret-square-down"></i>',
    'stopwatch':   '<i class="fas fa-fw fa-stopwatch"></i>',
    'clock':       '<i class="fas fa-fw fa-clock"></i>'
}
"""
Predefined list of selected `font-awesome <http://fontawesome.io/icons/>`__ icons
that are used throughout this application.
"""
