#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains common forms for MyDojo application.
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import urllib.parse

#
# Flask related modules.
#
import flask


#-------------------------------------------------------------------------------


def _is_safe_url(target):
    """
    Check, if the URL is safe enough to be redirected to.
    """
    ref_url  = urllib.parse.urlparse(flask.request.host_url)
    test_url = urllib.parse.urlparse(urllib.parse.urljoin(flask.request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

def _is_same_path(first, second):
    """
    Check, if both URL point to same path.
    """
    first_url  = urllib.parse.urlparse(first)
    second_url = urllib.parse.urlparse(second)
    return first_url.path == second_url.path

def get_redirect_target(target_url = None, default_url = None, exclude_url = None):
    """
    Get redirection target, either from GET request variable, or from referrer header.
    """
    options = (
        target_url,
        flask.request.form.get('next'),
        flask.request.args.get('next'),
        flask.request.referrer,
        default_url,
        flask.url_for('index')
    )
    for target in options:
        if not target:
            continue
        if _is_same_path(target, flask.request.base_url):
            continue
        if exclude_url and _is_same_path(target, exclude_url):
            continue
        if _is_safe_url(target):
            return target
    raise RuntimeError("Unable to choose apropriate redirection target.")
