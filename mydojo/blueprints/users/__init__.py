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

This pluggable module provides access to user account management features. These
features include:

* general user account listing
* detailed user account view
* creating new user accounts
* updating existing user accounts
* deleting existing user accounts
* enabling existing user accounts
* disabling existing user accounts
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


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
import mydojo.db
import mydojo.auth
from mydojo.base import HTMLMixin, SQLAlchemyMixin, ItemListView,\
    ItemShowView, ItemCreateView, ItemUpdateView, ItemEnableView,\
    ItemDisableView, ItemDeleteView, MyDojoBlueprint
from mydojo.db import UserModel
from mydojo.blueprints.users.forms import CreateUserAccountForm, UpdateUserAccountForm,\
    AdminUpdateUserAccountForm
from mydojo.mailer import MAILER


BLUEPRINT_NAME = 'users'
"""Name of the blueprint as module global constant."""


class UsersListView(HTMLMixin, SQLAlchemyMixin, ItemListView):
    """
    General user account listing.
    """
    methods = ['GET']

    authentication = True

    authorization = [mydojo.auth.PERMISSION_ADMIN]

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return lazy_gettext('User management')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`mydojo.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    @classmethod
    def get_action_menu(cls):
        """*Implementation* of :py:func:`mydojo.base.ItemListView.get_action_menu`."""
        action_menu = mydojo.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'create',
            endpoint = 'users.create',
            hidetitle = True
        )
        return action_menu

    @classmethod
    def get_context_action_menu(cls):
        """*Implementation* of :py:func:`mydojo.base.ItemListView.get_context_action_menu`."""
        action_menu = mydojo.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'show',
            endpoint = 'users.show',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'update',
            endpoint = 'users.update',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'disable',
            endpoint = 'users.disable',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'enable',
            endpoint = 'users.enable',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'delete',
            endpoint = 'users.delete',
            hidetitle = True
        )
        return action_menu


class UsersShowView(HTMLMixin, SQLAlchemyMixin, ItemShowView):
    """
    Detailed user account view.
    """
    methods = ['GET']

    authentication = True

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_icon`."""
        return 'action-show-user'

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return lazy_gettext('Show details of user account &quot;%(item)s&quot;', item = kwargs['item'].login)

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_title`."""
        return lazy_gettext('Show user account details')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`mydojo.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    @classmethod
    def authorize_item_action(cls, item):
        """
        Perform access authorization for current user to particular item.
        """
        # Each user must be able to view his/her account.
        permission_me = flask_principal.Permission(
            flask_principal.UserNeed(item.id)
        )
        # Managers of the groups the user is member of may view his/her account.
        needs = [mydojo.auth.ManagementNeed(x.id) for x in item.memberships]
        permission_mngr = flask_principal.Permission(*needs)
        return mydojo.auth.PERMISSION_ADMIN.can() or permission_mngr.can() or permission_me.can()

    @classmethod
    def get_action_menu(cls):
        """
        Get action menu for particular item.
        """
        action_menu = mydojo.menu.Menu()
        action_menu.add_entry(
            'endpoint',
            'update',
            endpoint = 'users.update',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'disable',
            endpoint = 'users.disable',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'enable',
            endpoint = 'users.enable',
            hidetitle = True
        )
        action_menu.add_entry(
            'endpoint',
            'delete',
            endpoint = 'users.delete',
            hidetitle = True
        )
        return action_menu


class UsersProfileView(UsersShowView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    Detailed user account view for currently logged-in user.
    """
    methods = ['GET']

    authentication = True

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'profile'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_icon`."""
        return 'profile'

    @classmethod
    def get_menu_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return lazy_gettext('My account')

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_url`."""
        return flask.url_for(cls.get_view_endpoint())

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_title`."""
        return lazy_gettext('My user account')

    @classmethod
    def get_view_template(cls):
        """*Implementation* of :py:func:`mydojo.base.RenderableView.get_view_template`."""
        return '{}/show.html'.format(BLUEPRINT_NAME)

    @classmethod
    def authorize_item_action(cls, item):
        """
        Perform access authorization for current user to particular item.
        """
        return True

    #---------------------------------------------------------------------------

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the *Flask* framework to service the request.

        Single item with given unique identifier will be retrieved from database
        and injected into template to be displayed to the user.
        """
        item_id = flask_login.current_user.get_id()
        return super().dispatch_request(item_id)


class UsersCreateView(HTMLMixin, SQLAlchemyMixin, ItemCreateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for creating new user accounts.
    """
    methods = ['GET','POST']

    authentication = True

    authorization = [mydojo.auth.PERMISSION_ADMIN]

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_icon`."""
        return 'action-create-user'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_title`."""
        return lazy_gettext('Create new user account')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`mydojo.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_success`."""
        return gettext(
            'User account <strong>%(item_id)s</strong> was successfully created.',
            item_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_failure`."""
        return gettext('Unable to create new user account.')

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_cancel`."""
        return gettext('Canceled creating new user account.')

    @staticmethod
    def get_item_form():
        """*Implementation* of :py:func:`mydojo.base.ItemCreateView.get_item_form`."""
        #
        # Inject list of choices for supported locales and roles. Another approach
        # would be to let the form get the list on its own, however that would create
        # dependency on application object.
        #
        roles = list(zip(flask.current_app.config['ROLES'], flask.current_app.config['ROLES']))
        locales = list(flask.current_app.config['MYDOJO_LOCALES'].items())

        return CreateUserAccountForm(
            choices_roles = roles,
            choices_locales = locales
        )


class UsersUpdateView(HTMLMixin, SQLAlchemyMixin, ItemUpdateView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for updating existing user accounts.
    """
    methods = ['GET','POST']

    authentication = True

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_icon`."""
        return 'action-update-user'

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return lazy_gettext('Update details of user account &quot;%(item)s&quot;', item = kwargs['item'].login)

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_title`."""
        return lazy_gettext('Update user account details')

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`mydojo.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    @classmethod
    def authorize_item_action(cls, item = None):
        """
        Perform access authorization for current user to particular item.
        """
        permission_me = flask_principal.Permission(
            flask_principal.UserNeed(item.id)
        )
        return mydojo.auth.PERMISSION_ADMIN.can() or permission_me.can()

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_success`."""
        return gettext(
            'User account <strong>%(item_id)s</strong> was successfully updated.',
            item_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_failure`."""
        return gettext(
            'Unable to update user account <strong>%(item_id)s</strong>.',
            item_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_cancel`."""
        return gettext(
            'Canceled updating user account <strong>%(item_id)s</strong>.',
            item_id = str(kwargs['item'])
        )

    @staticmethod
    def get_item_form(item):
        """*Implementation* of :py:func:`mydojo.base.ItemUpdateView.get_item_form`."""

        #
        # Inject list of choices for supported locales and roles. Another approach
        # would be to let the form get the list on its own, however that would create
        # dependency on application object.
        #
        roles = list(zip(flask.current_app.config['ROLES'], flask.current_app.config['ROLES']))
        locales = list(flask.current_app.config['MYDOJO_LOCALES'].items())

        admin = flask_login.current_user.has_role('admin')
        if not admin:
            form = UpdateUserAccountForm(
                choices_roles = roles,
                choices_locales = locales,
                obj = item
            )
        else:
            form = AdminUpdateUserAccountForm(
                choices_roles = roles,
                choices_locales = locales,
                db_item_id = item.id,
                obj = item
            )
        return form


class UsersEnableView(HTMLMixin, SQLAlchemyMixin, ItemEnableView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for enabling existing user accounts.
    """
    methods = ['GET','POST']

    authentication = True

    authorization = [mydojo.auth.PERMISSION_ADMIN]

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_icon`."""
        return 'action-enable-user'

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return lazy_gettext(
            'Enable user account &quot;%(item)s&quot;',
            item = kwargs['item'].login
        )

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`mydojo.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_success`."""
        return gettext(
            'User account <strong>%(item_id)s</strong> was successfully enabled.',
            item_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_failure`."""
        return gettext(
            'Unable to enable user account <strong>%(item_id)s</strong>.',
            item_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_cancel`."""
        return gettext(
            'Canceled enabling user account <strong>%(item_id)s</strong>.',
            item_id = str(kwargs['item'])
        )

    #---------------------------------------------------------------------------

    def do_after_action(self, item):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.do_after_action`."""
        mail_locale = item.locale
        if not mail_locale:
            mail_locale = flask.current_app.config['BABEL_DEFAULT_LOCALE']

        with force_locale(mail_locale):
            msg = flask_mail.Message(
                gettext(
                    "%(prefix)s Account activation - %(item_id)s",
                    prefix = flask.current_app.config['MAIL_SUBJECT_PREFIX'],
                    item_id = item.login
                ),
                recipients = [item.email],
                bcc = flask.current_app.config['MYDOJO_ADMINS']
            )
            msg.body = flask.render_template(
                'users/email_activation.txt',
                account = item
            )
            MAILER.send(msg)


class UsersDisableView(HTMLMixin, SQLAlchemyMixin, ItemDisableView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for deleting existing user accounts.
    """
    methods = ['GET','POST']

    authentication = True

    authorization = [mydojo.auth.PERMISSION_ADMIN]

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_icon`."""
        return 'action-disable-user'

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return lazy_gettext(
            'Disable user account &quot;%(item)s&quot;',
            item = kwargs['item'].login
        )

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`mydojo.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_success`."""
        return gettext(
            'User account <strong>%(item_id)s</strong> was successfully disabled.',
            item_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_failure`."""
        return gettext(
            'Unable to disable user account <strong>%(item_id)s</strong>.',
            item_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_cancel`."""
        return gettext(
            'Canceled disabling user account <strong>%(item_id)s</strong>.',
            item_id = str(kwargs['item'])
        )


class UsersDeleteView(HTMLMixin, SQLAlchemyMixin, ItemDeleteView):  # pylint: disable=locally-disabled,too-many-ancestors
    """
    View for deleting existing user accounts.
    """
    methods = ['GET','POST']

    authentication = True

    authorization = [mydojo.auth.PERMISSION_ADMIN]

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_icon`."""
        return 'action-delete-user'

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return lazy_gettext(
            'Delete user account &quot;%(item)s&quot;',
            item = kwargs['item'].login
        )

    #---------------------------------------------------------------------------

    @property
    def dbmodel(self):
        """*Implementation* of :py:func:`mydojo.base.SQLAlchemyMixin.dbmodel`."""
        return UserModel

    #---------------------------------------------------------------------------

    @staticmethod
    def get_message_success(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_success`."""
        return gettext(
            'User account <strong>%(item_id)s</strong> was successfully and permanently deleted.',
            item_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_failure(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_failure`."""
        return gettext(
            'Unable to delete user account <strong>%(item_id)s</strong>.',
            item_id = str(kwargs['item'])
        )

    @staticmethod
    def get_message_cancel(**kwargs):
        """*Implementation* of :py:func:`mydojo.base.ItemActionView.get_message_cancel`."""
        return gettext(
            'Canceled deleting user account <strong>%(item_id)s</strong>.',
            item_id = str(kwargs['item'])
        )


#-------------------------------------------------------------------------------


class UsersBlueprint(MyDojoBlueprint):
    """
    Pluggable module - users.
    """

    def register_app(self, app):
        """
        *Callback method*. Will be called from :py:func:`mydojo.base.MyDojoApp.register_blueprint`
        method and can be used to customize the Flask application object. Possible
        use cases:

        * application menu customization

        :param mydojo.base.MyDojoApp app: Flask application to be customize.
        """
        app.navbar_main.add_entry(
            'view',
            'admin.{}'.format(BLUEPRINT_NAME),
            position = 40,
            view = UsersListView
        )


#-------------------------------------------------------------------------------


def get_blueprint():
    """
    Mandatory interface and factory function. This function must return a valid
    instance of :py:class:`mydojo.base.MyDojoBlueprint` or :py:class:`flask.Blueprint`.
    """

    hbp = UsersBlueprint(
        BLUEPRINT_NAME,
        __name__,
        template_folder = 'templates',
        url_prefix = '/{}'.format(BLUEPRINT_NAME)
    )

    hbp.register_view_class(UsersListView,    '/')
    hbp.register_view_class(UsersCreateView,  '/create')
    hbp.register_view_class(UsersShowView,    '/<int:item_id>/show')
    hbp.register_view_class(UsersProfileView, '/profile')
    hbp.register_view_class(UsersUpdateView,  '/<int:item_id>/update')
    hbp.register_view_class(UsersEnableView,  '/<int:item_id>/enable')
    hbp.register_view_class(UsersDisableView, '/<int:item_id>/disable')
    hbp.register_view_class(UsersDeleteView,  '/<int:item_id>/delete')

    return hbp
