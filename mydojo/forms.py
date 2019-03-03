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
import wtforms
import flask
import flask_wtf
from flask_babel import gettext, lazy_gettext

import mydojo.const
import mydojo.db


def str_to_bool(value):
    """
    Convert given string value to boolean.
    """
    if str(value).lower() == 'true':
        return True
    if str(value).lower() == 'false':
        return False
    raise ValueError('Invalid string value {} to be converted to boolean'.format(str(value)))


def str_to_bool_with_none(value):
    """
    Convert given string value to boolean or ``None``.
    """
    if str(value).lower() == 'true':
        return True
    if str(value).lower() == 'false':
        return False
    if str(value).lower() == 'none':
        return None
    raise ValueError('Invalid string value {} to be converted to boolean'.format(str(value)))


def str_to_int_with_none(value):
    """
    Convert given string value to boolean or ``None``.
    """
    if str(value).lower() == 'none':
        return None
    try:
        return int(value)
    except:
        raise ValueError('Invalid string value {} to be converted to integer'.format(str(value)))


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
        flask.url_for('home.index')
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


def check_email(form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating user emails or account logins (usernames).
    """
    if mydojo.const.CRE_EMAIL.match(field.data):
        return
    raise wtforms.validators.ValidationError(
        gettext(
            'The "%(val)s" value does not look like valid email address.',
            val = str(field.data)
        )
    )

def check_unique_login(form, field):  # pylint: disable=locally-disabled,unused-argument
    """
    Callback for validating of uniqueness of user login.
    """
    user = mydojo.db.UserModel.query.filter_by(login = field.data).first()
    if user is not None:
        raise wtforms.validators.ValidationError(
            gettext(
                'Please use different login, the "%(val)s" is already taken.',
                val = str(field.data)
            )
        )


#-------------------------------------------------------------------------------


class BaseItemForm(flask_wtf.FlaskForm):
    """
    Class representing generic item action (create/update/delete) form for MyDojo
    application.

    This form contains support for redirection back to original page.
    """
    next = wtforms.HiddenField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate the redirection URL.
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    @staticmethod
    def is_multivalue(field_name):  # pylint: disable=locally-disabled,unused-argument
        """
        Check, if given form field is a multivalue field.

        :param str field_name: Name of the form field.
        :return: ``True``, if the field can contain multiple values, ``False`` otherwise.
        :rtype: bool
        """
        return False


class ItemActionConfirmForm(BaseItemForm):
    """
    Class representing generic item action confirmation form for MyDojo application.

    This form contains nothing else but two buttons, one for confirmation, one for
    canceling the delete action. Actual item identifier is passed as part of the URL.
    """
    submit = wtforms.SubmitField(
        lazy_gettext('Confirm')
    )
    cancel = wtforms.SubmitField(
        lazy_gettext('Cancel')
    )
