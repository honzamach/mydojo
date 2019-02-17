#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
Description
-----------

This pluggable module provides various utility and development tools including
official `Flask-DebugToolbar <https://flask-debugtoolbar.readthedocs.io/en/latest/>`__
extension.


Provided endpoints
------------------

``/devtools/config``
    Page providing view of current application configuration settings.

    * *Authentication:* authentication
    * *Authorization:* :py:const:`mydojo.auth.PERMISSION_DEVELOPER`
    * *Methods:* ``GET``
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


#
# Flask related modules.
#
import flask_debugtoolbar
from flask_babel import lazy_gettext

#
# Custom modules.
#
import mydojo.auth
from mydojo.base import HTMLMixin, SimpleView, MyDojoBlueprint


BLUEPRINT_NAME = 'devtools'
"""Name of the blueprint as module global constant."""


class ConfigView(HTMLMixin, SimpleView):
    """
    View for displaying current MyDojo application configuration and environment.
    """

    authentication = True

    authorization = [mydojo.auth.PERMISSION_DEVELOPER]

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'config'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_title`."""
        return lazy_gettext('View system configuration')

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return lazy_gettext('System configuration')


#-------------------------------------------------------------------------------


class DevtoolsBlueprint(MyDojoBlueprint):
    """
    Pluggable module - development tools (*devtools*).
    """

    def register_app(self, app):
        """
        *Callback method*. Will be called from :py:func:`mydojo.base.MyDojoApp.register_blueprint`
        method and can be used to customize the Flask application object. Possible
        use cases:

        * application menu customization

        :param mydojo.base.MyDojoApp app: Flask application to be customized.
        """
        self.developer_toolbar.init_app(app)

        app.navbar_main.add_entry(
            'view',
            'developer.devconfig',
            position = 10,
            view = ConfigView
        )


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`mydojo.base.MyDojoBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = DevtoolsBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.developer_toolbar = flask_debugtoolbar.DebugToolbarExtension()  # pylint: disable=locally-disabled,attribute-defined-outside-init

    hbp.register_view_class(ConfigView, '/config')

    return hbp
