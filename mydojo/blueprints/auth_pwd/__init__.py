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

This pluggable module provides classical web login form with password authentication
method.


Provided endpoints
------------------

``/auth_pwd/login``
    Page providing classical web login form.

    * *Authentication:* no authentication
    * *Methods:* ``GET``, ``POST``
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import sys
import traceback
import sqlalchemy

#
# Flask related modules.
#
import flask
import flask_login
import flask_principal
from flask_babel import gettext

#
# Custom modules.
#
import mydojo.const
import mydojo.forms
from mydojo.base import HTMLMixin, SQLAlchemyMixin, SimpleView, MyDojoBlueprint
from mydojo.db import UserModel
from mydojo.blueprints.auth_pwd.forms import LoginForm


BLUEPRINT_NAME = 'auth_pwd'
"""Name of the blueprint as module global constant."""


class LoginView(HTMLMixin, SQLAlchemyMixin, SimpleView):
    """
    View enabling classical password login.
    """
    methods = ['GET', 'POST']

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'login'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_icon`."""
        return 'login'

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`mydojo.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    @property
    def search_by(self):
        """*Implementation* of :py:func:`mydojo.base.SQLAlchemyMixin.search_by`."""
        return self.dbmodel.login

    def dispatch_request(self):
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the *Flask* framework to service the request.
        """
        if flask_login.current_user.is_authenticated:
            return self.redirect(
                default_url = flask.url_for(
                    flask.current_app.config['MYDOJO_LOGIN_REDIRECT']
                )
            )

        form = LoginForm()
        if form.validate_on_submit():
            try:
                user = self.fetch(form.login.data)

                # Check for password validity.
                if user.check_password(form.password.data):

                    # User account must be enabled.
                    if not user.enabled:
                        self.flash(
                            flask.Markup(gettext(
                                'Account for user <strong>%(login)s (%(name)s)</strong> is currently disabled, you may not login.',
                                login = user.login,
                                name = user.fullname
                            )),
                            mydojo.const.FLASH_FAILURE
                        )
                        self.abort(403)

                    flask_login.login_user(user)

                    # Tell Flask-Principal the identity changed. Access to private method
                    # _get_current_object is according to the Flask documentation:
                    #   http://flask.pocoo.org/docs/1.0/reqcontext/#notes-on-proxies
                    flask_principal.identity_changed.send(
                        flask.current_app._get_current_object(),   # pylint: disable=locally-disabled,protected-access
                        identity = flask_principal.Identity(user.get_id())
                    )

                    self.flash(
                        flask.Markup(gettext(
                            'You have been successfully logged in as <strong>%(user)s</strong>.',
                            user = str(user)
                        )),
                        mydojo.const.FLASH_SUCCESS
                    )
                    self.logger.info(
                        "User '{}' successfully logged in with 'auth_pwd'.".format(
                            user.login
                        )
                    )

                    # Redirect user back to original page.
                    return self.redirect(
                        default_url = flask.url_for(
                            flask.current_app.config['MYDOJO_LOGIN_REDIRECT']
                        )
                    )

                # Warn about invalid credentials in case of invalid password. Do
                # not say specifically it was password, that was invalid.
                self.flash(
                    gettext('You have entered wrong login credentials.'),
                    mydojo.const.FLASH_FAILURE
                )

            except sqlalchemy.orm.exc.MultipleResultsFound:
                self.logger.error(
                    "Multiple results found for user login '{}'.".format(
                        form.login.data
                    )
                )
                self.abort(500)

            except sqlalchemy.orm.exc.NoResultFound:
                self.flash(
                    gettext('You have entered wrong login credentials.'),
                    mydojo.const.FLASH_FAILURE
                )

            except Exception:  # pylint: disable=locally-disabled,broad-except
                self.flash(
                    gettext(
                        "Unable to perform password login as '{}'.".format(
                            form.login.data
                        )
                    ),
                    mydojo.const.FLASH_FAILURE
                )
                flask.current_app.log_exception_with_label(
                    traceback.TracebackException(*sys.exc_info()),
                    gettext('Unable to perform password login.'),
                )

        self.response_context.update(
            form = form,
            next = mydojo.forms.get_redirect_target()
        )
        return self.generate_response()


#-------------------------------------------------------------------------------


class PwdAuthBlueprint(MyDojoBlueprint):
    """
    Pluggable module - special developer authentication (*auth_pwd*).
    """

#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`mydojo.base.MyDojoBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = PwdAuthBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.register_view_class(LoginView, '/login')

    return hbp
