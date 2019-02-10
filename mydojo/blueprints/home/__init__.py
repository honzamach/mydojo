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

This pluggable module provides default home page.


Provided endpoints
------------------

``/``
    Page providing home page.

    * *Authentication:* no authentication
    * *Methods:* ``GET``
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


#
# Flask related modules.
#
from flask_babel import lazy_gettext

#
# Custom modules.
#
from mydojo.base import HTMLMixin, SimpleView, MyDojoBlueprint


BLUEPRINT_NAME = 'home'
"""Name of the blueprint as module global constant."""


class IndexView(HTMLMixin, SimpleView):
    """
    View presenting home page.
    """
    methods = ['GET']

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'index'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_icon`."""
        return 'module-home'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_title`."""
        return lazy_gettext('Welcome to MyDojo')

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return lazy_gettext('Home')


#-------------------------------------------------------------------------------


class HomeBlueprint(MyDojoBlueprint):
    """
    Pluggable module - home page (*home*).
    """

#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`mydojo.base.MyDojoBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = HomeBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates'
    )

    hbp.register_view_class(IndexView, '/')

    return hbp
