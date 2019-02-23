#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains default configurations for MyDojo application. One of the
classes defined in this module may be passed as argument to :py:func:`mydojo.app.create_app_full`
factory function to bootstrap MyDojo default configurations. These values may be
then optionally overwritten by external configuration file and/or additional
configuration file defined indirrectly via environment variable. Please refer to
the documentation of :py:func:`mydojo.app.create_app_full` factory function for
more details on this process.

There are following predefined configuration classess available:

:py:class:`mydojo.config.ProductionConfig`
    Default configuration suite for production environments.

:py:class:`mydojo.config.DevelopmentConfig`
    Default configuration suite for development environments.

:py:class:`mydojo.config.TestingConfig`
    Default configuration suite for testing environments.

There is also following constant structure containing mapping of simple configuration
names to configuration classess:

:py:const:`CONFIG_MAP`

It is used from inside of :py:func:`mydojo.app.create_app` factory method to pick
and apply correct configuration class to application. Please refer to the documentation
of :py:func:`mydojo.app.create_app` factory function for more details on this process.
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import socket
import collections

from flask_babel import lazy_gettext

#
# Custom modules.
#
import mydojo.const


APP_NAME = 'MyDojo'
APP_ID   = 'mydojo'


class BaseConfig:  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Base class for default configurations of MyDojo application. You are free to
    extend and customize contents of this class to provide better default values
    for your particular environment.

    The configuration keys must be a valid Flask configuration and so they must
    be written in UPPERCASE to be correctly recognized.
    """

    #---------------------------------------------------------------------------
    # Flask internal configurations. Please refer to Flask documentation for
    # more information about each configuration key.
    #---------------------------------------------------------------------------

    DEBUG      = False
    TESTING    = False
    SECRET_KEY = 'default-secret-key'

    #---------------------------------------------------------------------------
    # Flask extension configurations. Please refer to the documentation of that
    # particular Flask extension for more details.
    #---------------------------------------------------------------------------

    #
    # Flask-WTF configurations.
    #
    WTF_CSRF_ENABLED = True

    #
    # Flask-Mail configurations.
    #
    MAIL_SERVER         = 'localhost'
    MAIL_PORT           = 25
    MAIL_USERNAME       = None
    MAIL_PASSWORD       = None
    MAIL_DEFAULT_SENDER = '{}@{}'.format(APP_ID, socket.getfqdn())
    MAIL_SUBJECT_PREFIX = '[{}]'.format(APP_NAME)

    #
    # Flask-Babel configurations.
    #
    BABEL_DEFAULT_LOCALE   = mydojo.const.MYDOJO_DEFAULT_LOCALE
    BABEL_DEFAULT_TIMEZONE = mydojo.const.MYDOJO_DEFAULT_TIMEZONE

    #
    # Flask-SQLAlchemy configurations.
    #
    SQLALCHEMY_DATABASE_URI        = 'postgresql://{ident}:{ident}@localhost/{ident}'.format(ident = APP_ID)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #---------------------------------------------------------------------------
    # Custom application configurations.
    #---------------------------------------------------------------------------

    ROLES = mydojo.const.ROLES
    """List of all valid user roles supported by the application."""

    MYDOJO_LOGIN_VIEW = 'auth_pwd.login'
    """
    Default login view. Users will be redirected to this view in case they are not
    authenticated, but the authentication is required for the requested endpoint.
    """

    MYDOJO_LOGIN_MSGCAT = 'info'
    """Default message category for messages related to user authentication."""

    MYDOJO_ENDPOINT_HOME = 'home.index'
    """Homepage endpoint."""

    MYDOJO_LOGIN_REDIRECT = 'home.index'
    """Default redirection endpoint after login."""

    MYDOJO_LOGOUT_REDIRECT = 'home.index'
    """Default redirection endpoint after logout."""

    MYDOJO_LOCALES = collections.OrderedDict([
        ('en', 'English'),
        ('cs', 'Česky')
    ])
    """List of all languages (locales) supported by the application."""

    MYDOJO_MODULES = [
        'mydojo.blueprints.auth_pwd',
        'mydojo.blueprints.design',
        'mydojo.blueprints.home',
        'mydojo.blueprints.gadgets',
        'mydojo.blueprints.lab',
        'mydojo.blueprints.devtools'
    ]
    """List of requested application blueprints to be loaded during setup."""

    MYDOJO_DISABLED_ENDPOINTS = []
    """List of application-wide disabled endpoints."""

    MYDOJO_LOG_DEFAULT_LEVEL = 'info'
    """Default logging level, case insensitive. One of the values ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``."""

    MYDOJO_LOG_FILE = '/var/log/mydojo.log'
    """Log file settings for logging framework."""

    MYDOJO_LOG_FILE_LEVEL = 'info'
    """File logging level, case insensitive. One of the values ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``."""

    MYDOJO_LOG_EMAIL_LEVEL = 'error'
    """File logging level, case insensitive. One of the values ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL``."""

    MYDOJO_NAVBAR_MAIN = [
        {
            'entry_type': 'submenu',
            'ident': 'dashboards',
            'position': 100,
            'title': lazy_gettext('Dashboards'),
            'resptitle': True,
            'icon': 'section-dashboards'
        },
        {
            'entry_type': 'submenu',
            'ident': 'more',
            'position': 200,
            'title': lazy_gettext('More'),
            'resptitle': True,
            'icon': 'section-more',
        },
        {
            'entry_type': 'submenu',
            'ident': 'admin',
            'position': 300,
            'authentication': True,
            'authorization': ['admin'],
            'title': lazy_gettext('Administration'),
            'resptitle': True,
            'icon': 'section-administration'
        },
        {
            'entry_type': 'submenu',
            'ident': 'developer',
            'position': 400,
            'authentication': True,
            'authorization': ['developer'],
            'title': lazy_gettext('Development'),
            'resptitle': True,
            'icon': 'section-development'
        }
    ]
    """Configuration of main application navbar skeleton."""

    MYDOJO_ADMINS = ['root']
    """List of system administrator emails."""


class ProductionConfig(BaseConfig):  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Class containing application configurations for *production* environment.
    """


class DevelopmentConfig(BaseConfig):  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Class containing application configurations for *development* environment.
    """

    #---------------------------------------------------------------------------
    # Flask internal configurations. Please refer to Flask documentation for
    # more information about each configuration key.
    #---------------------------------------------------------------------------

    DEBUG = True
    """Overwrite default :py:const:`mydojo.config.Config.DEBUG`."""

    #---------------------------------------------------------------------------
    # Custom application configurations.
    #---------------------------------------------------------------------------

    MYDOJO_MODULES = [
        'mydojo.blueprints.auth_dev',
        'mydojo.blueprints.auth_pwd',
        'mydojo.blueprints.design',
        'mydojo.blueprints.home',
        'mydojo.blueprints.gadgets',
        'mydojo.blueprints.lab',
        'mydojo.blueprints.devtools'
    ]
    """Overwrite default :py:const:`mydojo.config.Config.MYDOJO_MODULES`."""

    MYDOJO_LOG_DEFAULT_LEVEL = 'debug'
    """Overwrite default :py:const:`mydojo.config.Config.MYDOJO_LOG_DEFAULT_LEVEL`."""

    MYDOJO_LOG_FILE = '/var/tmp/mydojo-dev.py.log'
    """Overwrite default :py:const:`mydojo.config.Config.MYDOJO_LOG_FILE`."""

    MYDOJO_LOG_FILE_LEVEL = 'debug'
    """Overwrite default :py:const:`mydojo.config.Config.MYDOJO_LOG_FILE_LEVEL`."""


class TestingConfig(BaseConfig):  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Class containing *testing* Mydojo applications` configurations.
    """

    #---------------------------------------------------------------------------
    # Flask internal configurations. Please refer to Flask documentation for
    # more information about each configuration key.
    #---------------------------------------------------------------------------

    TESTING = True
    """Overwrite default :py:const:`mydojo.config.Config.TESTING`."""


CONFIG_MAP = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
    'default':     ProductionConfig
}
"""Configuration map for easy mapping of configuration aliases to config objects."""
