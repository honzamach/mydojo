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

This pluggable module provides special authentication method, that is particularly
usable for developers and enables them to impersonate any user.

After enabling this module special authentication endpoint will be available
and will provide simple authentication form with a list of all currently available
user accounts. It will be possible for any user to log into the application as
any other user without entering password.

This module is disabled by default in *production* environment and enabled by
default in *development* environment.

.. warning::

    This module *must never ever be enabled on production* systems, because it is
    a huge security risk and enables possible access control management violation.
    You have been warned!


Provided endpoints
------------------

``/auth_dev/login``
    Page providing special developer login form.

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
from mydojo.base import HTMLViewMixin, SQLAlchemyViewMixin, MyDojoSimpleView, MyDojoBlueprint
from mydojo.db import UserModel
from mydojo.blueprints.auth_dev.forms import LoginForm


BLUEPRINT_NAME = 'auth_dev'
"""Name of the blueprint as module global constant."""


class LoginView(HTMLViewMixin, SQLAlchemyViewMixin, MyDojoSimpleView):
    """
    View enabling special developer login.
    """
    methods = ['GET', 'POST']

    @classmethod
    def get_view_name(cls):
        """
        *Interface implementation* of :py:func:`mydojo.base.MyDojoBaseView.get_view_name`.
        """
        return 'login'

    @classmethod
    def get_view_icon(cls):
        """
        *Interface implementation* of :py:func:`mydojo.base.MyDojoBaseView.get_view_icon`.
        """
        return 'login'

    @property
    def dbmodel(self):
        """
        *Interface implementation* of :py:func:`mydojo.base.SQLAlchemyViewMixin.dbmodel`.
        """
        return UserModel

    def dispatch_request(self):
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the *Flask* framework to service the request.
        """
        form = LoginForm()

        if form.validate_on_submit():
            try:
                user = self.fetch(form.login.data.get_id())
                if not user.enabled:
                    self.flash(
                        flask.Markup(gettext(
                            'Please be aware, that the account for user <strong>%(login)s (%(name)s)</strong> is currently disabled.',
                            login = user.login,
                            name = user.fullname
                        )),
                        mydojo.const.FLASH_WARNING
                    )

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
                    "User '{}' successfully logged in with 'auth_dev'.".format(
                        user.login
                    )
                )

                # Redirect user back to original page.
                return self.redirect(default_url = flask.url_for('index'))

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
                        "Unable to perform developer login as '{}'.".format(
                            form.login.data
                        )
                    ),
                    mydojo.const.FLASH_FAILURE
                )
                flask.current_app.log_exception_with_label(
                    traceback.TracebackException(*sys.exc_info()),
                    gettext('Unable to perform developer login.'),
                )

        self.response_context.update(
            form = form,
            next = mydojo.forms.get_redirect_target()
        )
        return self.generate_response()


#-------------------------------------------------------------------------------


class DevAuthBlueprint(MyDojoBlueprint):
    """
    Pluggable module - special developer authentication (*auth_dev*).
    """

#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`mydojo.base.MyDojoBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = DevAuthBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.register_view_class(LoginView, '/login')

    return hbp
