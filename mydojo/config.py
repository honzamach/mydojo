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
classes defined in this module may be passed as argument to :py:func:`mydojo.app.create_app`
factory function to bootstrap MyDojo default configurations. These values may be
then optionally overwritten by external configuration file and/or additional
configuration file defined indirrectly via environment variable. Please refer to
the documentation of :py:func:`mydojo.app.create_app` factory function for more
details on this process.

There are following predefined configuration classess available:

:py:class:`mydojo.config.ProductionConfig`
    Default configuration suite for production environments.

:py:class:`mydojo.config.DevelopmentConfig`
    Default configuration suite for development environments.

:py:class:`mydojo.config.TestingConfig`
    Default configuration suite for testing environments.

"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import socket
import collections

from flask_babel import lazy_gettext

#
# Custom modules.
#
import mydojo.const


class Config:  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Base class for default MyDojo application configurations. You are free to
    extend and customize contents of this class to provide better default values
    for your particular environment.

    The configuration keys must be a valid Flask configuration and so they must
    be written in UPPERCASE to be correctly recognized
    """

    #---------------------------------------------------------------------------

    #
    # Flask internal configurations. Please refer to Flask documentation for
    # more information about each confiuration key.
    #

    DEBUG      = False
    TESTING    = False
    SECRET_KEY = 'default-secret-key'

    #---------------------------------------------------------------------------

    #
    # Flask extension configurations.
    #

    # WTForms configurations.
    WTF_CSRF_ENABLED = True

    # Mail server settings for logging framework.
    MAIL_SERVER         = 'localhost'
    MAIL_PORT           = 25
    MAIL_USERNAME       = None
    MAIL_PASSWORD       = None
    MAIL_DEFAULT_SENDER = 'mydojo@{}'.format(socket.getfqdn())

    # Babel configurations for application localization.
    BABEL_DEFAULT_LOCALE   = mydojo.const.MYDOJO_DEFAULT_LOCALE
    BABEL_DEFAULT_TIMEZONE = mydojo.const.MYDOJO_DEFAULT_TIMEZONE

    # SQLAlchemy configurations.
    SQLALCHEMY_DATABASE_URI        = 'postgresql://mydojo:mydojo@localhost/mydojo'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #---------------------------------------------------------------------------

    #
    # MyDojo custom configurations.
    #

    ROLES = [
        mydojo.const.ROLE_USER,
        mydojo.const.ROLE_DEVELOPER,
        mydojo.const.ROLE_ADMIN
    ]
    """List of all user roles supported by the MyDojo application."""

    MYDOJO_LOGIN_VIEW = 'auth_dev.login'
    """Default login view."""

    MYDOJO_LOGIN_MSGCAT = 'info'
    """Default login message category."""

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
    """List of all languages (locales) supported by the MyDojo application."""

    MYDOJO_MODULES = [
        'mydojo.blueprints.auth_pwd',
        'mydojo.blueprints.design',
        'mydojo.blueprints.home',
        'mydojo.blueprints.lab'
    ]
    """List of requested application blueprints to be loaded during setup."""

    MYDOJO_LOG_FILE = '/var/log/mydojo.log'
    """Log file settings for logging framework."""

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
            'authorization': ['power'],
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


class ProductionConfig(Config):  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Class containing *production* MyDojo applications` configurations.
    """
    pass


class DevelopmentConfig(Config):  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Class containing *development* MyDojo applications` configurations.
    """

    #---------------------------------------------------------------------------

    #
    # Flask internal configurations. Please refer to Flask documentation for
    # more information about each confiuration key.
    #

    DEBUG = True
    """Overwritten default value from :py:const:`mydojo.config.Config.DEBUG`"""

    #---------------------------------------------------------------------------

    #
    # MyDojo custom configurations.
    #

    MYDOJO_MODULES = [
        'mydojo.blueprints.auth_dev',
        'mydojo.blueprints.auth_pwd',
        'mydojo.blueprints.design',
        'mydojo.blueprints.home',
        'mydojo.blueprints.lab'
    ]
    """Overwritten default value from :py:const:`mydojo.config.Config.MYDOJO_MODULES`"""

    MYDOJO_LOG_FILE = '/var/tmp/mydojo-dev.py.log'
    """Overwritten default value from :py:const:`mydojo.config.Config.MYDOJO_LOG_FILE`"""


class TestingConfig(Config):  # pylint: disable=locally-disabled,too-few-public-methods
    """
    Class containing *testing* Mydojo applications` configurations.
    """

    #---------------------------------------------------------------------------

    #
    # Flask internal configurations. Please refer to Flask documentation for
    # more information about each confiuration key.
    #

    TESTING = True
    """Overwritten default value from :py:const:`mydojo.config.Config.TESTING`"""


CONFIG_MAP = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
    'default':     ProductionConfig
}
