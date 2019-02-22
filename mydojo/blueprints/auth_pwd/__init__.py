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

``/auth_pwd/register``
    Page providing new user account registration form.

    * *Authentication:* no authentication
    * *Methods:* ``GET``, ``POST``

"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import sys
import datetime
import traceback
import sqlalchemy

#
# Flask related modules.
#
import flask
import flask_login
import flask_principal
import flask_mail
from flask_babel import gettext, lazy_gettext, force_locale

#
# Custom modules.
#
import mydojo.const
import mydojo.forms
from mydojo.base import HTMLMixin, SQLAlchemyMixin, SimpleView, MyDojoBlueprint
from mydojo.db import UserModel
from mydojo.mailer import MAILER
from mydojo.blueprints.auth_pwd.forms import LoginForm, RegistrationForm


BLUEPRINT_NAME = 'auth_pwd'
"""Name of the blueprint as module global constant."""


class LoginView(HTMLMixin, SQLAlchemyMixin, SimpleView):
    """
    View providing classical password login.
    """
    methods = ['GET', 'POST']

    is_sign_in = True

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'login'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_icon`."""
        return 'login'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_title`."""
        return lazy_gettext('Password login')

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return lazy_gettext('Login (pwd)')

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
                                'Your user account <strong>%(login)s (%(name)s)</strong> is currently disabled, you are not permitted to log in.',
                                login = user.login,
                                name = user.fullname
                            )),
                            mydojo.const.FLASH_FAILURE
                        )
                        self.abort(403)

                    flask_login.login_user(user)

                    # Mark the login time into database.
                    user.logintime = datetime.datetime.utcnow()
                    self.dbsession.commit()

                    # Tell Flask-Principal the identity changed. Access to private method
                    # _get_current_object is according to the Flask documentation:
                    #   http://flask.pocoo.org/docs/1.0/reqcontext/#notes-on-proxies
                    flask_principal.identity_changed.send(
                        flask.current_app._get_current_object(),   # pylint: disable=locally-disabled,protected-access
                        identity = flask_principal.Identity(user.get_id())
                    )

                    self.flash(
                        flask.Markup(gettext(
                            'You have been successfully logged in as <strong>%(login)s (%(name)s)</strong>.',
                            login = user.login,
                            name = user.fullname
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
                    flask.Markup(gettext(
                        "Unable to perform password login as <strong>%(user)s</strong>.",
                        user = str(form.login.data)
                    )),
                    mydojo.const.FLASH_FAILURE
                )
                flask.current_app.log_exception_with_label(
                    traceback.TracebackException(*sys.exc_info()),
                    'Unable to perform password login.',
                )

        self.response_context.update(
            form = form,
            next = mydojo.forms.get_redirect_target()
        )
        return self.generate_response()


class RegisterView(HTMLMixin, SQLAlchemyMixin, SimpleView):
    """
    View enabling classical password login.
    """
    methods = ['GET', 'POST']

    is_sign_up = True

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'register'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_icon`."""
        return 'register'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_title`."""
        return lazy_gettext('Register new account')

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return lazy_gettext('Register (pwd)')

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

        form = RegistrationForm(
            choices_locales = list(flask.current_app.config['MYDOJO_LOCALES'].items())
        )

        if form.validate_on_submit():
            form_data = form.data

            if form_data[mydojo.const.FORM_ACTION_CANCEL]:
                self.flash(
                    gettext('Account registration canceled.'),
                    mydojo.const.FLASH_INFO
                )
                return self.redirect(
                    default_url = flask.url_for(
                        flask.current_app.config['MYDOJO_ENDPOINT_HOME']
                    )
                )

            if form_data[mydojo.const.FORM_ACTION_SUBMIT]:
                try:
                    # Populate the user object from form data and make sure the
                    # account has default 'user' role and is disabled by default.
                    item = UserModel()
                    form.populate_obj(item)
                    item.roles = [mydojo.const.ROLE_USER]
                    item.enabled = False

                    self.dbsession.add(item)
                    self.dbsession.commit()

                    # Send information about new account registration to system
                    # admins. Use default locale for email content translations.
                    mail_locale = flask.current_app.config['BABEL_DEFAULT_LOCALE']
                    with force_locale(mail_locale):
                        msg = flask_mail.Message(
                            gettext(
                                "%(prefix)s Account registration - %(item_id)s",
                                prefix  = flask.current_app.config['MAIL_SUBJECT_PREFIX'],
                                item_id = item.login
                            ),
                            recipients = flask.current_app.config['MYDOJO_ADMINS']
                        )
                        msg.body = flask.render_template(
                            'auth_pwd/email_registration_admins.txt',
                            account = item,
                            justification = form_data['justification']
                        )
                        MAILER.send(msg)

                    # Send information about new account registration to the user.
                    # Use user`s preferred locale for email content translations.
                    mail_locale = item.locale
                    if not mail_locale:
                        mail_locale = flask.current_app.config['BABEL_DEFAULT_LOCALE']
                    with force_locale(mail_locale):
                        msg = flask_mail.Message(
                            gettext(
                                "%(prefix)s Account registration - %(item_id)s",
                                prefix  = flask.current_app.config['MAIL_SUBJECT_PREFIX'],
                                item_id = item.login
                            ),
                            recipients = [item.email]
                        )
                        msg.body = flask.render_template(
                            'auth_pwd/email_registration_user.txt',
                            account = item,
                            justification = form_data['justification']
                        )
                        MAILER.send(msg)

                    self.flash(
                        flask.Markup(gettext(
                            'User account <strong>%(login)s (%(name)s)</strong> was successfully registered.',
                            login = item.login,
                            name = item.fullname
                        )),
                        mydojo.const.FLASH_SUCCESS
                    )
                    self.logger.info(
                        "New user account '{}' was successfully registered with 'auth_pwd'.".format(
                            item.login
                        )
                    )
                    return self.redirect(
                        default_url = flask.url_for(
                            flask.current_app.config['MYDOJO_ENDPOINT_HOME']
                        )
                    )

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    self.flash(
                        gettext('Unable to register new user account.'),
                        mydojo.const.FLASH_FAILURE
                    )
                    flask.current_app.log_exception_with_label(
                        traceback.TracebackException(*sys.exc_info()),
                        'Unable to register new user account.',
                    )

        self.response_context.update(
            form_url = flask.url_for('{}.{}'.format(
                self.module_name,
                self.get_view_name()
            )),
            form = form
        )
        return self.generate_response()


#-------------------------------------------------------------------------------


class PwdAuthBlueprint(MyDojoBlueprint):
    """
    Pluggable module - classical password authentication (*auth_pwd*).
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

    hbp.register_view_class(LoginView,    '/login')
    hbp.register_view_class(RegisterView, '/register')

    return hbp
