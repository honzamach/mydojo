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


FORM_ACTION_SUBMIT = 'submit'
"""Name of the form *submit* button."""

FORM_ACTION_CANCEL = 'cancel'
"""Name of the form *cancel* button."""


ACTION_ITEM_CREATE = 'create'
"""Name of the item *create* action."""

ACTION_ITEM_UPDATE = 'update'
"""Name of the item *update* action."""

ACTION_ITEM_ENABLE = 'enable'
"""Name of the item *enable* action."""

ACTION_ITEM_DISABLE = 'disable'
"""Name of the item *disable* action."""

ACTION_ITEM_DELETE = 'delete'
"""Name of the item *delete* action."""


ROLE_USER = 'user'
"""Name of the 'user' role."""

ROLE_DEVELOPER = 'developer'
"""Name of the 'developer' role."""

ROLE_ADMIN = 'admin'
"""Name of the 'admin' role."""

ROLE_ANY = 'any'
"""Name of the 'any' role."""

ROLES = [
    ROLE_USER,
    ROLE_DEVELOPER,
    ROLE_ADMIN
]
"""List of valid user roles."""


CFGKEY_MODULES_REQUESTED = 'MYDOJO_MODULES'
"""Configuration key name: List of all requested blueprints."""

CFGKEY_MYDOJO_NAVBAR_MAIN = 'MYDOJO_NAVBAR_MAIN'
"""Configuration key name: skeleton of main application navigation bar."""


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
    'profile':      '<i class="fas fa-fw fa-clipboard-user"></i>',
    'register':     '<i class="fas fa-fw fa-user-plus"></i>',
    'help':         '<i class="fas fa-fw fa-question-circle"></i>',
    'language':     '<i class="fas fa-fw fa-globe"></i>',
    'debug':        '<i class="fas fa-fw fa-bug"></i>',

    #
    # User role icons.
    #
    'role-anonymous':  '<i class="fas fa-fw fa-user-secret"></i>',
    'role-user':       '<i class="fas fa-fw fa-user"></i>',
    'role-developer':  '<i class="fas fa-fw fa-user-md"></i>',
    'role-maintainer': '<i class="fas fa-fw fa-user-tie"></i>',
    'role-admin':      '<i class="fas fa-fw fa-user-ninja"></i>',

    #
    # Main navbar section icons.
    #
    'section-dashboards':     '<i class="fas fa-fw fa-tachometer-alt"></i>',
    'section-more':           '<i class="fas fa-fw fa-puzzle-piece"></i>',
    'section-administration': '<i class="fas fa-fw fa-cogs"></i>',
    'section-development':    '<i class="fas fa-fw fa-bug"></i>',

    #
    # Built-in pluggable module icons.
    #
    'module-auth-api': '<i class="fas fa-fw fa-key"></i>',
    'module-auth-dev': '<i class="fas fa-fw fa-key"></i>',
    'module-auth-pwd': '<i class="fas fa-fw fa-key"></i>',
    'module-design':   '<i class="fas fa-fw fa-palette"></i>',
    'module-home':     '<i class="fas fa-fw fa-home"></i>',
    'module-blog':     '<i class="fas fa-fw fa-journal-whills"></i>',
    'module-gadgets':  '<i class="fas fa-fw fa-tools"></i>',
    'module-lab':      '<i class="fas fa-fw fa-flask"></i>',
    'module-devtools': '<i class="fas fa-fw fa-bug"></i>',

    #
    # Built-in action icons.
    #
    'modal-question':      '<i class="fas fa-fw fa-question-circle"></i>',
    'actions':             '<i class="fas fa-fw fa-wrench"></i>',
    'action-more':         '<i class="fas fa-fw fa-cubes"></i>',
    'action-search':       '<i class="fas fa-fw fa-search"></i>',
    'action-show':         '<i class="fas fa-fw fa-eye"></i>',
    'action-show-user':    '<i class="fas fa-fw fa-user-circle"></i>',
    'action-create':       '<i class="fas fa-fw fa-plus-circle"></i>',
    'action-create-user':  '<i class="fas fa-fw fa-user-plus"></i>',
    'action-update':       '<i class="fas fa-fw fa-edit"></i>',
    'action-update-user':  '<i class="fas fa-fw fa-user-edit"></i>',
    'action-enable':       '<i class="fas fa-fw fa-unlock"></i>',
    'action-enable-user':  '<i class="fas fa-fw fa-user-check"></i>',
    'action-disable':      '<i class="fas fa-fw fa-lock"></i>',
    'action-disable-user': '<i class="fas fa-fw fa-user-lock"></i>',
    'action-delete':       '<i class="fas fa-fw fa-trash"></i>',
    'action-delete-user':  '<i class="fas fa-fw fa-user-slash"></i>',
    'action-save':         '<i class="fas fa-fw fa-save"></i>',
    'action-download':     '<i class="fas fa-fw fa-file-download"></i>',
    'action-download-zip': '<i class="fas fa-fw fa-file-archive"></i>',
    'action-download-csv': '<i class="fas fa-fw fa-file-csv"></i>',
    'action-download-svg': '<i class="fas fa-fw fa-file-image"></i>',
    'action-download-js':  '<i class="fab fa-fw fa-js"></i>',
    'action-mail':         '<i class="fas fa-fw fa-envelope"></i>',
    'action-reload':       '<i class="fas fa-fw fa-sync-alt"></i>',
    'action-genkey':       '<i class="fas fa-fw fa-key"></i>',

    'item-enabled':  '<i class="fas fa-fw fa-toggle-on"></i>',
    'item-disabled': '<i class="fas fa-fw fa-toggle-off"></i>',

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
    'calendar':    '<i class="fas fa-fw fa-calendar-alt"></i>',
    'stopwatch':   '<i class="fas fa-fw fa-stopwatch"></i>',
    'clock':       '<i class="fas fa-fw fa-clock"></i>',
    'check':       '<i class="fas fa-fw fa-check-square"></i>',
    'check_blank': '<i class="far fa-fw fa-square"></i>',
    'ok':          '<i class="fas fa-fw fa-check"></i>',
    'ko':          '<i class="fas fa-fw fa-times"></i>',
    'sortasc':     '<i class="fas fa-fw fa-sort-asc"></i>',
    'sortdesc':    '<i class="fas fa-fw fa-sort-desc"></i>',
    'backtotop':   '<i class="fas fa-fw fa-level-up-alt"></i>',
    'first':       '<i class="fas fa-fw fa-angle-double-left"></i>',
    'previous':    '<i class="fas fa-fw fa-angle-left"></i>',
    'next':        '<i class="fas fa-fw fa-angle-right"></i>',
    'last':        '<i class="fas fa-fw fa-angle-double-right" aria-hidden="true"></i>',
    'liitem':      '<i class="fas fa-li fa-asterisk" aria-hidden="true"></i>',
    'expand':      '<i class="fas fa-fw fa-angle-left" aria-hidden="true"></i>',
    'collapse':    '<i class="fas fa-fw fa-angle-down" aria-hidden="true"></i>',
    'form-error':  '<i class="fas fa-fw fa-exclamation-triangle" aria-hidden="true"></i>'
}
"""
Predefined list of selected `font-awesome <http://fontawesome.io/icons/>`__ icons
that are used throughout this application.
"""
