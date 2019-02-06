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

This pluggable module provides default application desing and style. Currently
there are no views provided by this module.


.. note::

    To completely change the design of the whole application you can implement
    your own custom _design_ module and replace this one. However this requires
    that you thoroughly study the design of this module and provide your own
    implementation for all API hooks, otherwise you may break the whole application.


Module content
--------------

#. Base Jinja2 template providing application layout.
#. Common macros for Jinja2 templates.
#. Common forms (delete, disable, enable).
#. HTML error pages (400, 403, 404, 410, 500).
#. Various images
#. Application CSS styles
#. Application JavaScripts

"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import mydojo.base


#
# Name of the blueprint as module global constant.
#
BLUEPRINT_NAME = 'design'


class DesignBlueprint(mydojo.base.MyDojoBlueprint):
    """
    Pluggable module - default application design and style.
    """

#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`mydojo.base.MyDojoBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = DesignBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        static_folder   = 'static',
        static_url_path = '/static/design'
    )

    return hbp
