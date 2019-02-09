#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains custom developer login form for Hawat.
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


#
# Flask related modules.
#
import wtforms
import flask_wtf
from flask_babel import lazy_gettext

#
# Custom modules.
#
from mydojo.forms import check_email


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
