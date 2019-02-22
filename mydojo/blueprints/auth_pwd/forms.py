#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains classical password authentication login form.
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import pytz

#
# Flask related modules.
#
import wtforms
import flask_wtf
from flask_babel import lazy_gettext

#
# Custom modules.
#
from mydojo.forms import check_email, check_unique_login


class LoginForm(flask_wtf.FlaskForm):
    """
    Class representing classical password authentication login form.
    """
    login = wtforms.StringField(
        lazy_gettext('Login:'),
        validators = [
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min = 3, max = 50),
            check_email
        ]
    )
    password = wtforms.PasswordField(
        lazy_gettext('Password:'),
        validators = [
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min = 8),
        ]
    )
    submit = wtforms.SubmitField(
        lazy_gettext('Login')
    )
    cancel = wtforms.SubmitField(
        lazy_gettext('Cancel')
    )


class RegistrationForm(flask_wtf.FlaskForm):
    """
    Class representing classical account registration form.
    """
    login = wtforms.StringField(
        lazy_gettext('Login:'),
        validators = [
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min = 3, max = 50),
            check_email,
            check_unique_login
        ]
    )
    fullname = wtforms.StringField(
        lazy_gettext('Full name:'),
        validators = [
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min = 3, max = 100)
        ]
    )
    email = wtforms.StringField(
        lazy_gettext('Email:'),
        validators = [
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min = 3, max = 250),
            check_email
        ]
    )
    password = wtforms.PasswordField(
        lazy_gettext('Password:'),
        validators = [
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min = 8),
        ]
    )
    password2 = wtforms.PasswordField(
        lazy_gettext('Repeat Password:'),
        validators = [
            wtforms.validators.DataRequired(),
            wtforms.validators.EqualTo('password'),
        ]
    )
    locale = wtforms.SelectField(
        lazy_gettext('Prefered locale:'),
        validators = [
            wtforms.validators.Optional()
        ],
        choices = [('', lazy_gettext('<< no preference >>'))],
        filters = [lambda x: x or None]
    )
    timezone = wtforms.SelectField(
        lazy_gettext('Prefered timezone:'),
        validators = [
            wtforms.validators.Optional(),
        ],
        choices = [('', lazy_gettext('<< no preference >>'))] + list(zip(pytz.common_timezones, pytz.common_timezones)),
        filters = [lambda x: x or None]
    )

    justification = wtforms.TextAreaField(
        lazy_gettext('Justification:'),
        validators = [
            wtforms.validators.DataRequired(),
            wtforms.validators.Length(min = 10, max = 500)
        ]
    )

    submit = wtforms.SubmitField(
        lazy_gettext('Register')
    )
    cancel = wtforms.SubmitField(
        lazy_gettext('Cancel')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #
        # Handle additional custom keywords.
        #

        # The list of choices for 'locale' attribute comes from outside of the
        # form to provide as loose tie as possible to the outer application.
        # Another approach would be to load available choices here with:
        #
        #   locales = list(flask.current_app.config['SUPPORTED_LOCALES'].items())
        #
        # That would mean direct dependency on flask.Flask application though.
        self.locale.choices[1:] = kwargs['choices_locales']
