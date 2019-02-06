#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains core application features for MyDojo.

The most important feture of this module is the :py:func:`mydojo.app.create_app`
factory method, that is responsible for bootstrapping the whole application (see
its documentation for more details).
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import os
import datetime
import jinja2
from babel import Locale

#
# Flask related modules.
#
import flask
import flask_babel
import flask_jsglue

#
# Custom modules.
#
import mydojo.base
import mydojo.const
import mydojo.log
import mydojo.forms


#-------------------------------------------------------------------------------


def _setup_app_logging(app):
    """
    Setup logging to file and via email for given MyDojo application. Logging
    capabilities are adjustable by application configuration.

    :param mydojo.base.MyDojoApp app: MyDojo application to be modified.
    :return: Modified MyDojo application
    :rtype: mydojo.base.MyDojoApp
    """
    mydojo.log.setup_logging_file(app)

    return app


def _setup_app_core(app):
    """
    Setup application core for given MyDojo application. The application core
    contains following features:

        * Error handlers
        * Default routes
        * Additional custom Jinja template variables
        * Additional custom Jinja template macros

    :param mydojo.base.MyDojoApp app: MyDojo application to be modified.
    :return: Modified MyDojo application
    :rtype: mydojo.base.MyDojoApp
    """
    @app.errorhandler(400)
    def eh_badrequest(err):  # pylint: disable=locally-disabled,unused-variable
        """Flask error handler to be called to service HTTP 400 error."""
        return flask.render_template('errors/e400.html', error_obj = err), 400

    @app.errorhandler(403)
    def eh_forbidden(err):  # pylint: disable=locally-disabled,unused-variable
        """Flask error handler to be called to service HTTP 403 error."""
        return flask.render_template('errors/e403.html', error_obj = err), 403

    @app.errorhandler(404)
    def eh_page_not_found(err):  # pylint: disable=locally-disabled,unused-variable
        """Flask error handler to be called to service HTTP 404 error."""
        return flask.render_template('errors/e404.html', error_obj = err), 404

    @app.errorhandler(410)
    def eh_gone(err):  # pylint: disable=locally-disabled,unused-variable
        """Flask error handler to be called to service HTTP 410 error."""
        return flask.render_template('errors/e410.html', error_obj = err), 410

    @app.errorhandler(500)
    def eh_internal_server_error(err):  # pylint: disable=locally-disabled,unused-variable
        """Flask error handler to be called to service HTTP 500 error."""
        return flask.render_template('errors/e500.html', error_obj = err), 500

    @app.before_request
    def before_request():  # pylint: disable=locally-disabled,unused-variable
        """
        Use Flask`s :py:func:`flask.Flask.before_request` hook for performing
        various usefull tasks before each request.
        """
        flask.g.requeststart = datetime.datetime.utcnow()

    @app.context_processor
    def jinja_inject_variables():  # pylint: disable=locally-disabled,unused-variable
        """
        Inject additional variables into Jinja2 global template namespace.
        """
        return dict(
            mydojo_version     = mydojo.__version__,
            mydojo_current_app = flask.current_app,
            mydojo_logger      = flask.current_app.logger,
            mydojo_cdt_utc     = datetime.datetime.utcnow(),
            mydojo_cdt_local   = datetime.datetime.now(),
        )

    @app.context_processor
    def jinja2_inject_functions():  # pylint: disable=locally-disabled,unused-variable,too-many-locals
        """
        Register additional helpers into Jinja2 global template namespace. This
        function will install following helpers:

        get_icon
            Reference for :py:func:`mydojo.app.get_icon`

        get_datetime_utc
            Reference for :py:func:`mydojo.app.get_datetime_utc`

        get_datetime_local
            Reference for :py:func:`mydojo.app.get_datetime_local`
        """
        def get_icon(icon_name, default_icon = 'missing-icon'):
            """
            Get HTML icon markup for given icon. The icon will be looked up in
            the :py:const:`mydojo.const.FA_ICONS` lookup table.

            :param str icon_name: Name of the icon.
            :param str default_icon: Name of the default icon.
            :return: Icon including HTML markup.
            :rtype: flask.Markup
            """
            return flask.Markup(
                mydojo.const.FA_ICONS.get(
                    icon_name,
                    mydojo.const.FA_ICONS.get(default_icon)
                )
            )

        def get_country_flag(country):
            """
            Get URL to static country flag file.

            :param str country: Name of the icon.
            :return: Country including HTML markup.
            :rtype: flask.Markup
            """
            if not mydojo.const.CRE_COUNTRY_CODE.match(country):
                return get_icon('flag')

            return flask.Markup(
                '<img src="{}">'.format(
                    flask.url_for(
                        'design.static',
                        filename = 'images/country-flags/flags-iso/shiny/16/{}.png'.format(
                            country.upper()
                        )
                    )
                )
            )

        def get_timedelta(tstamp):
            """
            Get timedelta from current UTC time and given datetime object.

            :param datetime.datetime: Datetime of the lower timedelta boundary.
            :return: Timedelta object.
            :rtype: datetime.timedelta
            """
            return datetime.datetime.utcnow() - tstamp

        def get_datetime_utc():
            """
            Get current UTC datetime.

            :return: Curent UTC datetime.
            :rtype: datetime.datetime
            """
            return datetime.datetime.utcnow()

        def get_datetime_local():
            """
            Get current local timestamp.

            :return: Curent local timestamp.
            :rtype: datetime.datetime
            """
            return datetime.datetime.now()

        def check_file_exists(filename):
            """
            Check, that given file exists in the filesystem.

            :param str filename: Name of the file to check.
            :return: Existence flag as ``True`` or ``False``.
            :rtype: bool
            """
            return os.path.isfile(filename)

        def include_raw(filename):
            """
            Include given file in raw form directly into the generated content.
            This may be usefull for example for including JavaScript files
            directly into the HTML page.
            """
            return jinja2.Markup(
                app.jinja_loader.get_source(app.jinja_env, filename)[0]
            )

        return dict(
            get_icon          = get_icon,
            get_country_flag  = get_country_flag,

            get_timedelta      = get_timedelta,
            get_datetime_utc   = get_datetime_utc,
            get_datetime_local = get_datetime_local,

            check_file_exists = check_file_exists,

            include_raw = include_raw
        )

    class MyDojoJSONEncoder(flask.json.JSONEncoder):
        """
        Custom JSON encoder for converting anything into JSON strings.
        """
        def default(self, obj):  # pylint: disable=locally-disabled,method-hidden,arguments-differ
            try:
                if isinstance(obj, datetime.datetime):
                    return obj.isoformat() + 'Z'
            except:  # pylint: disable=locally-disabled,bare-except
                pass
            try:
                return obj.to_dict()
            except:  # pylint: disable=locally-disabled,bare-except
                pass
            try:
                return str(obj)
            except:  # pylint: disable=locally-disabled,bare-except
                pass
            return flask.json.JSONEncoder.default(self, obj)

    app.json_encoder = MyDojoJSONEncoder

    @app.route('/')
    def index():  # pylint: disable=locally-disabled,unused-variable
        """
        Default route for index page.
        """
        return flask.render_template('index.html')

    @app.route('/mydojo-main.js')
    def mainjs():  # pylint: disable=locally-disabled,unused-variable
        """
        Default route for main application JavaScript file.
        """
        return flask.make_response(
            flask.render_template('mydojo-main.js'),
            200,
            {'Content-Type': 'text/javascript'}
        )

    # Initialize JSGlue plugin for using `flask.url_for()` method in JavaScript.
    jsglue = flask_jsglue.JSGlue()
    jsglue.init_app(app)

    return app


def _setup_app_babel(app):
    """
    Setup application`s internationalization sybsystem.

    :param mydojo.base.MyDojoApp app: MyDojo application to be modified.
    :return: Modified MyDojo application
    :rtype: mydojo.base.MyDojoApp
    """
    babel = flask_babel.Babel(app)
    app.set_resource(mydojo.const.RESOURCE_BABEL, babel)

    @app.route('/locale/<code>')
    def locale(code):  # pylint: disable=locally-disabled,unused-variable
        """
        Application route providing users with the option of changing locale.
        """
        if code not in flask.current_app.config['MYDOJO_LOCALES']:
            return flask.abort(404)

        flask.session['locale'] = code
        flask_babel.refresh()

        flask.flash(
            flask.Markup(flask_babel.gettext(
                'Locale was succesfully changed to <strong>%(lcln)s (%(lclc)s)</strong>.',
                lclc = code,
                lcln = flask.current_app.config['MYDOJO_LOCALES'][code]
            )),
            mydojo.const.FLASH_SUCCESS
        )

        # Redirect user back to original page.
        return flask.redirect(
            mydojo.forms.get_redirect_target(
                default_url = flask.url_for('index')
            )
        )

    @babel.localeselector
    def get_locale():  # pylint: disable=locally-disabled,unused-variable
        """
        Implementation of locale selector for :py:mod:`flask_babel`.
        """
        # Store the best locale selection into the session.
        if 'locale' not in flask.session:
            flask.session['locale'] = flask.request.accept_languages.best_match(app.config['MYDOJO_LOCALES'].keys())

        return flask.session['locale']

    @babel.timezoneselector
    def get_timezone():  # pylint: disable=locally-disabled,unused-variable
        """
        Implementation of timezone selector for :py:mod:`flask_babel`.
        """
        # Store the default timezone selection into the session.
        if 'timezone' not in flask.session:
            flask.session['timezone'] = flask.current_app.config['BABEL_DEFAULT_TIMEZONE']

        return flask.session['timezone']

    @app.before_request
    def before_request():  # pylint: disable=locally-disabled,unused-variable
        """
        Use Flask`s :py:func:`flask.Flask.before_request` hook for storing
        currently selected locale and timezone to request`s global storage.
        """
        flask.g.locale   = flask.session.get('locale', get_locale())
        flask.g.timezone = flask.session.get('timezone', get_timezone())

    def babel_format_bytes(size, unit = 'B', step_size = 1024):
        """
        Format given numeric value to human readable string describing size in
        B/KB/MB/GB/TB.

        :param int size: Number to be formatted.
        :param enum unit: Starting unit, possible values are ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB'].
        :param int step_size: Size of the step between units.
        :return: Formatted and localized string.
        :rtype: string
        """
        units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']
        idx_max = len(units) - 1
        unit = unit.upper()
        for idx, val in enumerate(units):
            # Skip the last step, there is no next unit defined after exabyte.
            if idx == idx_max:
                break
            if size > step_size:
                if unit == val:
                    size = size / step_size
                    unit = units[idx+1]
            else:
                break
        return '{} {}'.format(
            flask_babel.format_decimal(size),
            unit
        )

    def babel_translate_locale(locale_id, with_current = False):
        """
        Translate given locale language. By default return language in locale`s
        language. Optionaly return language in given locale`s language.
        """
        locale_obj = Locale.parse(locale_id)
        if not with_current:
            return locale_obj.language_name
        return locale_obj.get_language_name(flask_babel.get_locale())

    def babel_language_in_locale(locale_id = 'en'):
        """
        Translate given locale language. By default return language in locale`s
        language. Optionaly return language in given locale`s language.
        """
        locale_obj = Locale.parse(flask_babel.get_locale())
        return locale_obj.get_language_name(locale_id)

    @app.context_processor
    def utility_processor():  # pylint: disable=locally-disabled,unused-variable
        """
        Register additional helpers into Jinja global namespace. This function
        will install following helpers:

        babel_format_datetime
            Reference for :py:func`flask_babel.format_datetime`

        babel_format_timedelta
            Reference for :py:func:`flask_babel.format_timedelta`
        """

        return dict(
            babel_format_datetime    = flask_babel.format_datetime,
            babel_format_timedelta   = flask_babel.format_timedelta,
            babel_format_decimal     = flask_babel.format_decimal,
            babel_format_percent     = flask_babel.format_percent,
            babel_format_bytes       = babel_format_bytes,
            babel_translate_locale   = babel_translate_locale,
            babel_language_in_locale = babel_language_in_locale
        )

    return app


def _setup_app_blueprints(app):
    """
    Setup application blueprints.

    :param mydojo.base.MyDojoApp app: MyDojo application to be modified.
    :return: Modified MyDojo application
    :rtype: mydojo.base.MyDojoApp
    """
    app.register_blueprints()

    return app


#-------------------------------------------------------------------------------


def create_app(
        config_dict   = None,
        config_object = 'mydojo.config.ProductionConfig',
        config_file   = '/etc/mydojo/mydojo.conf',
        config_env    = 'MYDOJO_CONFIG_FILE'):
    """
    Factory function for building MyDojo application. This function takes number of
    optional arguments, that can be used to create a very customized instance of
    MyDojo application. This can be very usefull when extending applications`
    capabilities or for purposes of testing. Each of these arguments has default
    value for the most common application setup, so for disabling it entirely it
    is necessary to provide ``None`` as a value.

    :param dict config_dict: Initial default configurations.
    :param str config_object: Name of the class or module containing configurations.
    :param str config_file: Name of the file containing configurations.
    :param str config_env:  Name of the environment variable pointing to file containing configurations.
    :return: MyDojo application
    :rtype: mydojo.base.MyDojoApp
    """

    app = mydojo.base.MyDojoApp('mydojo')

    if config_dict and isinstance(config_dict, dict):
        app.config.update(config_dict)
    if config_object:
        app.config.from_object(config_object)
    if config_file:
        app.config.from_pyfile(config_file, silent = True)
    if config_env:
        app.config.from_envvar(config_env, silent = True)

    _setup_app_logging(app)
    _setup_app_core(app)
    _setup_app_babel(app)
    _setup_app_blueprints(app)

    return app
