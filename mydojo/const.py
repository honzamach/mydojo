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


ROLE_USER = 'user'
"""Name of the 'user' role."""

ROLE_DEVELOPER = 'developer'
"""Name of the 'developer' role."""

ROLE_ADMIN = 'admin'
"""Name of the 'admin' role."""

ROLE_ANY = 'any'
"""Name of the 'any' role."""

ROLES = [ROLE_USER, ROLE_DEVELOPER, ROLE_ADMIN]
"""List of valid user roles."""


CFGKEY_MODULES_LOADED = 'MYDOJO_MODULES_LOADED'
"""Configuration key name: Registry of all successfully loaded blueprints."""

CFGKEY_MODULES_REQUESTED = 'MYDOJO_MODULES'
"""Configuration key name: List of all requested blueprints."""


RESOURCE_BABEL = 'babel'
"""Name for the ``flask_babel.Babel`` object within the application resources."""

RESOURCE_SQLDB = 'sqldb'
"""Name for the ``flask_sqlalchemy.SQLAlchemy`` object within the application resources."""

RESOURCE_MIGRATE = 'migrate'
"""Name for the ``flask_migrate.Migrate`` object within the application resources."""

RESOURCE_LOGIN_MANAGER = 'login_manager'
"""Name for the ``flask_login.LoginManager`` object within the application resources."""

RESOURCE_PRINCIPAL = 'principal'
"""Name for the ``flask_principal.Principal`` object within the application resources."""

ICON_NAME_MISSING_ICON = 'missing-icon'
"""Name of the icon to display instead of missing icons."""

FA_ICONS = {

    #
    # General icons.
    #
    'missing-icon': '<i class="fas fa-fw fa-question" title="Missing icon"></i>',
    'login':        '<i class="fas fa-fw fa-sign-in-alt"></i>',
    'logout':       '<i class="fas fa-fw fa-sign-out-alt"></i>',
    'register':     '<i class="fas fa-fw fa-user-plus"></i>',
    'help':         '<i class="fas fa-fw fa-question-circle"></i>',
    'language':     '<i class="fas fa-fw fa-globe"></i>',

    'role-anonymous':  '<i class="fas fa-fw fa-user-secret"></i>',
    'role-user':       '<i class="fas fa-fw fa-user"></i>',
    'role-developer':  '<i class="fas fa-fw fa-user-md"></i>',
    'role-maintainer': '<i class="fas fa-fw fa-user-tie"></i>',
    'role-admin':      '<i class="fas fa-fw fa-user-ninja"></i>',

    #
    # Main site section icons.
    #
    'section-dashboards':     '<i class="fas fa-fw fa-tachometer-alt"></i>',
    'section-more':           '<i class="fas fa-fw fa-puzzle-piece"></i>',
    'section-administration': '<i class="fas fa-fw fa-cogs"></i>',
    'section-development':    '<i class="fas fa-fw fa-bug"></i>',

    #
    # Built-in module icons.
    #
    'module-home':   '<i class="fas fa-fw fa-home"></i>',
    'module-design': '<i class="fas fa-fw fa-palette"></i>',
    'module-lab':    '<i class="fas fa-fw fa-flask"></i>',


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
