#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains special developer login form.
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


#
# Flask related modules.
#
import wtforms
from wtforms.ext.sqlalchemy.fields import QuerySelectField

import flask_wtf
from flask_babel import lazy_gettext

#
# Custom modules.
#
import mydojo.db


def get_available_users():
    """
    Query the database for list of all available users.
    """
    return mydojo.db.SQLDB.session.query(
        mydojo.db.UserModel
    ).order_by(
        mydojo.db.UserModel.login
    ).all()


class LoginForm(flask_wtf.FlaskForm):
    """
    Class representing developer authentication login form. This form provides
    list of all currently existing user accounts in simple selectbox, so that
    the developer can quickly login as different user.
    """
    login = QuerySelectField(
        lazy_gettext('User account:'),
        query_factory = get_available_users,
        get_label = lambda x: "{} ({}, #{})".format(x.fullname, x.login, x.id),
        validators = [
            wtforms.validators.DataRequired()
        ]
    )
    submit = wtforms.SubmitField(
        lazy_gettext('Login')
    )
    cancel = wtforms.SubmitField(
        lazy_gettext('Cancel')
    )
