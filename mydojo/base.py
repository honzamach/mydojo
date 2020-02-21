#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains implementations of base classes for MyDojo application pluggable
modules. Since the MyDojo application is based on excelent `Flask <http://flask.pocoo.org/>`__
microframework, the modularity and extendability of the application is already
built-in as `blueprint <http://flask.pocoo.org/docs/1.0/blueprints/>`__
feature. However this module provides customized classes for application,
blueprint and view, that provide some additional features that are out of the
scope of bare Flask microframework.

Module contents
---------------

* :py:class:`MyDojoApp`
* :py:class:`MyDojoBlueprint`
* :py:class:`HTMLMixin`
* :py:class:`AJAXMixin`
* :py:class:`SQLAlchemyMixin`
* :py:class:`BaseView`

    * :py:class:`FileNameView`
    * :py:class:`FileIDView`
    * :py:class:`RenderableView`

        * :py:class:`SimpleView`
        * :py:class:`ItemSearchView`
        * :py:class:`ItemListView`
        * :py:class:`ItemShowView`
        * :py:class:`ItemActionView`

            * :py:class:`ItemCreateView`
            * :py:class:`ItemUpdateView`
            * :py:class:`ItemDeleteView`
            * :py:class:`ItemChangeView`

                * :py:class:`ItemEnableView`
                * :py:class:`ItemDisableView`
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import sys
import datetime
import weakref
import traceback

#
# Flask related modules.
#
import sqlalchemy
import werkzeug.routing
import werkzeug.utils
import flask
import flask.app
import flask.views
import flask_login
from flask_babel import gettext

#
# Custom modules.
#
import mydojo.const
import mydojo.db
import mydojo.menu
import mydojo.errors
from mydojo.forms import get_redirect_target, ItemActionConfirmForm


class MyDojoAppException(Exception):
    """
    Custom class for :py:class:`mydojo.base.MyDojoApp` application exceptions.
    """

class MyDojoApp(flask.Flask):
    """
    Custom implementation of :py:class:`flask.Flask` class. This class extends the
    capabilities of the base class with following additional features:

    Configuration based blueprint registration
        The application configuration file contains a directive describing list
        of requested blueprints/modules, that should be registered into the
        application. This enables administrator to very easily fine tune the
        application setup for each installation. See the :py:func:`mydojo.base.MyDojoApp.register_blueprints`
        for more information on the topic.
    """

    def __init__(self, import_name, **kwargs):
        super().__init__(import_name, **kwargs)

        self.csrf = None

        self.navbar_main = mydojo.menu.Menu()

        self.sign_ins     = {}
        self.sign_ups     = {}
        self.resources    = {}

    @flask.app.setupmethod
    def add_url_rule(self, rule, endpoint = None, view_func = None, provide_automatic_options = None, **options):
        """
        Reimplementation of :py:func:`flask.Flask.add_url_rule` method. This method
        is capable of disabling selected application endpoints. Keep in mind, that
        some URL rules (like application global 'static' endpoint) are created during
        the :py:func:`flask.app.Flask.__init__` method and cannot be disabled,
        because at that point the configuration of the application is not yet loaded.
        """
        if self.config.get('DISABLED_ENDPOINTS', None) and self.config['DISABLED_ENDPOINTS'] and endpoint:
            if endpoint in self.config['DISABLED_ENDPOINTS']:
                self.logger.warning(
                    "Application endpoint '%s' is disabled by configuration.",
                    endpoint
                )
                return
        super().add_url_rule(rule, endpoint, view_func, provide_automatic_options, **options)

    def register_blueprint(self, blueprint, **options):
        """
        Reimplementation of :py:func:`flask.Flask.register_blueprint` method. This
        method will perform standart blueprint registration and on top of that will
        perform following additional tasks:

            * Register blueprint into custom internal registry. The registry lies
              within application`s ``config`` under key :py:const:`mydojo.const.CFGKEY_MODULES_REQUESTED`.
            * Call blueprint`s ``register_app`` method, if available, with ``self`` as only argument.

        :param mydojo.base.MyDojoBlueprint blueprint: Blueprint to be registered.
        :param dict options: Additional options, will be passed down to :py:func:`flask.Flask.register_blueprint`.
        """
        super().register_blueprint(blueprint, **options)

        if isinstance(blueprint, MyDojoBlueprint):
            if hasattr(blueprint, 'register_app'):
                blueprint.register_app(self)

            self.sign_ins.update(blueprint.sign_ins)
            self.sign_ups.update(blueprint.sign_ups)

    def register_blueprints(self):
        """
        Register all configured application blueprints. The configuration comes
        from :py:const:`mydojo.const.CFGKEY_MODULES_REQUESTED` configuration
        subkey, which must contain list of string names of required blueprints.
        The blueprint module must provide ``get_blueprint`` factory method, that
        must return valid instance of :py:class:`mydojo.base.MydojOblueprint`. This
        method will call the :py:func:`mydojo.base.MyDojoApp.register_blueprint` for
        each blueprint, that is being registered into the application.

        :raises mydojo.base.MyDojoAppException: In case the factory method ``get_blueprint`` is not provided by loaded module.
        """
        for name in self.config[mydojo.const.CFGKEY_MODULES_REQUESTED]:
            mod = werkzeug.utils.import_string(name)
            if hasattr(mod, 'get_blueprint'):
                self.register_blueprint(mod.get_blueprint())
            else:
                raise MyDojoAppException(
                    "Invalid pluggable module '{}', does not provide the 'get_blueprint' factory method.".format(name)
                )

    def log_exception_with_label(self, tbexc, label = ''):
        """
        Log given exception traceback into application logger.
        """
        self.logger.error('%s%s', label, ''.join(tbexc.format()))  # pylint: disable=locally-disabled,no-member

    def has_endpoint(self, endpoint):
        """
        Check if given routing endpoint is available.

        :param str endpoint: Application routing endpoint.
        :return: ``True`` in case endpoint exists, ``False`` otherwise.
        :rtype: bool
        """
        return endpoint in self.view_functions

    def get_endpoint_class(self, endpoint, quiet = False):
        """
        Get reference to view class registered to given routing endpoint.

        :param str endpoint: Application routing endpoint.
        :return: Reference to view class.
        :rtype: class
        """
        if not endpoint in self.view_functions:
            if quiet:
                return None
            raise MyDojoAppException(
                "Unknown endpoint name '{}'.".format(endpoint)
            )
        try:
            return self.view_functions[endpoint].view_class
        except AttributeError:
            return DecoratedView(self.view_functions[endpoint])


    def can_access_endpoint(self, endpoint, item = None):
        """
        Check, that the current user can access given endpoint/view.

        :param str endpoint: Application routing endpoint.
        :param item: Optional item.
        :return: ``True`` in case user can access the endpoint, ``False`` otherwise.
        :rtype: bool
        """
        try:
            view_class = self.get_endpoint_class(endpoint)

            # Reject unauthenticated users in case view requires authentication.
            if view_class.authentication:
                if not flask_login.current_user.is_authenticated:
                    return False

            # Check view authorization rules.
            if view_class.authorization:
                for auth_rule in view_class.authorization:
                    if not auth_rule.can():
                        return False

            # Check item action authorization callback, if exists.
            if hasattr(view_class, 'authorize_item_action'):
                if not view_class.authorize_item_action(item):
                    return False

            return True

        except MyDojoAppException:
            return False

    def get_resource(self, name):
        """
        Return reference to given registered resource.

        :param str name: Name of the resource.
        """
        return self.resources[name]()

    def set_resource(self, name, resource):
        """
        Store reference to given resource.

        :param str name: Name of the resource.
        :param resource: Resource to be registered.
        """
        self.resources[name] = weakref.ref(resource)


class MyDojoBlueprint(flask.Blueprint):
    """
    Custom implementation of :py:class:`flask.Blueprint` class. This class extends
    the capabilities of the base class with additional features:

        * Support for better integration into application and registration of view classes.
        * Support for custom tweaking of application object.
        * Support for custom style of authentication and authorization decorators
    """
    def __init__(self, name, import_name, **kwargs):
        super().__init__(name, import_name, **kwargs)

        self.sign_ins     = {}
        self.sign_ups     = {}

    def register_app(self, app):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        *Hook method:* Custom callback, which will be called from
        :py:func:`mydojo.base.MyDojoApp.register_blueprint` method and which can
        perform additional tweaking of MyDojo application object.

        :param mydojo.base.MyDojoApp app: Application object.
        """
        return

    def register_view_class(self, view_class, route_spec):
        """
        Register given view class into the internal blueprint registry.

        :param mydojo.base.BaseView view_class: View class (not instance!)
        :param str route_spec: Routing information for the view.
        """
        view_class.module_ref  = weakref.ref(self)
        view_class.module_name = self.name

        # Obtain view function.
        view_func = view_class.as_view(view_class.get_view_name())

        # Apply authentication decorators (if requested).
        if view_class.authentication:
            view_func = flask_login.login_required(view_func)

        # Apply authorization decorators (if requested).
        if view_class.authorization:
            for auth in view_class.authorization:
                view_func = auth.require(403)(view_func)

        # Register endpoint to the application.
        self.add_url_rule(route_spec, view_func = view_func)

        # Register SIGN IN and SIGN UP views to enable further special handling.
        if hasattr(view_class, 'is_sign_in') and view_class.is_sign_in:
            self.sign_ins[view_class.get_view_endpoint()] = view_class
        if hasattr(view_class, 'is_sign_up') and view_class.is_sign_up:
            self.sign_ups[view_class.get_view_endpoint()] = view_class


#-------------------------------------------------------------------------------


class HTMLMixin:
    """
    Mixin class enabling rendering responses as HTML. Use it in your custom view
    classess based on :py:class:`mydojo.base.RenderableView` to provide the
    ability to render Jinja2 template files into HTML responses.
    """

    @staticmethod
    def abort(status_code, message = None):  # pylint: disable=locally-disabled,unused-argument
        """
        Abort request processing with ``flask.abort`` function and custom status
        code and optional additional message. Return response as HTML document.
        """
        flask.abort(status_code, message)

    def flash(self, message, level = 'info'):  # pylint: disable=locally-disabled,no-self-use
        """
        Display a one time message to the user. This implementation uses the
        :py:func:`flask.flash` method.

        :param str message: Message text.
        :param str level: Level of the flash message.
        """
        flask.flash(message, level)

    def redirect(self, target_url = None, default_url = None, exclude_url = None):  # pylint: disable=locally-disabled,no-self-use
        """
        Redirect user to different page. This implementation uses the
        :py:func:`flask.redirect` method to return valid HTTP redirection response.

        :param str target_url: Explicit redirection target, if possible.
        :param str default_url: Default redirection URL to use in case it cannot be autodetected from the response.
        :param str exclude_url: URL to which to never redirect (for example never redirect back to the item detail after the item deletion).
        """
        return flask.redirect(
            get_redirect_target(target_url, default_url, exclude_url)
        )

    def generate_response(self, view_template = None):
        """
        Generate the response appropriate for this view class, in this case HTML
        page.

        :param str view_template: Override internally preconfigured page template.
        """
        return flask.render_template(
            view_template or self.get_view_template(),
            **self.response_context
        )


class AJAXMixin:
    """
    Mixin class enabling rendering responses as JSON documents. Use it in your
    custom view classess based on based on :py:class:`mydojo.base.RenderableView`
    to provide the ability to generate JSON responses.
    """

    @staticmethod
    def process_response_context(response_context):
        """
        Perform additional mangling with the response context before generating
        the response. This method can be useful to delete some context keys, that
        should not leave the server.

        :param dict response_context: Response context.
        :return: Possibly updated response context.
        :rtype: dict
        """
        return response_context

    @staticmethod
    def abort(status_code, message = None):
        """
        Abort request processing with ``flask.abort`` function and custom status
        code and optional additional message. Return response as JSON document.
        """
        flask.abort(
            mydojo.errors.api_error_response(status_code, message)
        )

    def flash(self, message, level = 'info'):  # pylint: disable=locally-disabled,no-self-use
        """
        Display a one time message to the user. This implementation uses the
        ``flash_messages`` subkey in returned JSON document to store the messages.

        :param str message: Message text.
        :param str level: Level of the flash message.
        """
        self.response_context.\
            setdefault('flash_messages', {}).\
            setdefault(level, []).\
            append(message)

    def redirect(self, target_url = None, default_url = None, exclude_url = None):  # pylint: disable=locally-disabled,no-self-use
        """
        Redirect user to different page. This implementation stores the redirection
        target to the JSON response.

        :param str target_url: Explicit redirection target, if possible.
        :param str default_url: Default redirection URL to use in case it cannot be autodetected from the response.
        :param str exclude_url: URL to which to never redirect (for example never redirect back to the item detail after the item deletion).
        """
        self.response_context.update(
            redirect = get_redirect_target(target_url, default_url, exclude_url)
        )
        return flask.jsonify(
            self.process_response_context(self.response_context)
        )

    def generate_response(self, view_template = None):  # pylint: disable=locally-disabled,unused-argument
        """
        Generate the response appropriate for this view class, in this case JSON
        document.

        :param str view_template: Override internally preconfigured page template.
        """
        return flask.jsonify(
            self.process_response_context(self.response_context)
        )

class SQLAlchemyMixin:
    """
    Mixin class providing generic interface for interacting with SQL database
    backend through SQLAlchemy library.
    """

    @property
    def dbmodel(self):
        """
        This property must be implemented in each subclass to return reference to
        appropriate model class based on *SQLAlchemy* declarative base.
        """
        raise NotImplementedError()

    @property
    def fetch_by(self):
        """
        Return model`s attribute (column) according to which to search for the item.
        """
        return self.dbmodel.id

    @property
    def dbsession(self):
        """
        This property contains the reference to current *SQLAlchemy* database session.
        """
        return mydojo.db.SQLDB.session

    def dbquery(self, dbmodel = None):
        """
        This property contains the reference to *SQLAlchemy* query object appropriate
        for particular ``dbmodel`` property.
        """
        return self.dbsession.query(dbmodel or self.dbmodel)

    def dbcolumn_min(self, dbcolumn):
        """
        Find and return the minimal value for given table column.
        """
        result = self.dbsession.query(sqlalchemy.func.min(dbcolumn)).one_or_none()
        if result:
            return result[0]
        return None

    def dbcolumn_max(self, dbcolumn):
        """
        Find and return the maximal value for given table column.
        """
        result = self.dbsession.query(sqlalchemy.func.max(dbcolumn)).one_or_none()
        if result:
            return result[0]
        return None

    @staticmethod
    def build_query(query, model, form_args):  # pylint: disable=locally-disabled,unused-argument
        """
        Modify given query according to the given arguments.
        """
        return query

    def fetch(self, item_id, fetch_by = None):
        """
        Fetch item with given primary identifier from the database.
        """
        fetch_by = fetch_by or self.fetch_by
        return self.dbquery().filter(fetch_by == item_id).one()

    def fetch_first(self, item_id, fetch_by = None):
        """
        Fetch item with given primary identifier from the database.
        """
        fetch_by = fetch_by or self.fetch_by
        return self.dbquery().filter(fetch_by == item_id).first()

    def search(self, form_args):
        """
        Perform actual search with given query.
        """
        query = self.build_query(self.dbquery(), self.dbmodel, form_args)

        # Adjust the query according to the paging parameters.
        if 'limit' in form_args and form_args['limit']:
            query = query.limit(int(form_args['limit']))
            if 'page' in form_args and form_args['page'] and int(form_args['page']) > 1:
                query = query.offset(
                    (int(form_args['page']) - 1) * int(form_args['limit'])
                )

        return query.all()


#-------------------------------------------------------------------------------


class BaseView(flask.views.View):
    """
    Base class for all custom MyDojo application views.
    """

    module_ref = None
    """
    Weak reference to parent module of this view.
    """

    module_name = None
    """
    Name of the parent module (blueprint). Will be set up during the process
    of registering the view into the blueprint in :py:func:`mydojo.base.MyDojoBlueprint.register_view_class`.
    """

    authentication = False
    """
    Similar to the ``decorators`` mechanism in Flask pluggable views, you may use
    this class variable to specify, that the view is protected by authentication.
    During the process of registering the view into the blueprint in
    :py:func:`mydojo.base.MyDojoBlueprint.register_view_class` the view will be
    automatically decorated with :py:func:`flask_login.login_required` decorator.

    The advantage of using this in favor of ``decorators`` is that the application
    menu can automatically hide/show items inaccessible to current user.

    This is a scalar variable that must contain boolean ``True`` or ``False``.
    """

    authorization  = ()
    """
    Similar to the ``decorators`` mechanism in Flask pluggable views, you may use
    this class variable to specify, that the view is protected by authorization.
    During the process of registering the view into the blueprint in
    :py:func:`mydojo.base.MyDojoBlueprint.register_view_class` the view will be
    automatically decorated with given authorization decorators.

    The advantage of using this in favor of ``decorators`` is that the application
    menu can automatically hide/show items inaccessible to current user.

    This is a list variable that must contain list of desired decorators.
    """

    @classmethod
    def get_view_name(cls):
        """
        Return unique name for the view. Name must be unique in the namespace of
        parent blueprint/module and should contain only characters ``[a-z0-9]``.
        It will be used for generating endpoint name for the view.

        *This method does not have any default implementation and must be overridden
        by a subclass.*

        :return: Name for the view.
        :rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def get_view_endpoint(cls):
        """
        Return name of the routing endpoint for the view within the whole application.

        Default implementation generates the endpoint name by concatenating the
        module name and view name.

        :return: Routing endpoint for the view within the whole application.
        :rtype: str
        """
        return '{}.{}'.format(cls.module_name, cls.get_view_name())

    @classmethod
    def get_view_url(cls, **kwargs):
        """
        Return view URL.

        :param dict kwargs: Optional parameters.
        :return: URL for the view.
        :rtype: str
        """
        return flask.url_for(cls.get_view_endpoint(), **kwargs)

    @classmethod
    def get_view_icon(cls):
        """
        Return menu entry icon name for the view. Given name will be used as index
        to built-in icon registry.

        Default implementation generates the icon name by concatenating the prefix
        ``module-`` with module name.

        :return: View icon.
        :rtype: str
        """
        return 'module-{}'.format(cls.module_name)

    @classmethod
    def get_view_title(cls, **kwargs):
        """
        Return title for the view, that will be displayed in the ``title`` tag of
        HTML ``head`` element and also as the content of page header in ``h2`` tag.

        Default implementation returns the return value of :py:func:`mydojo.base.BaseView.get_menu_title`
        method by default.

        :param dict kwargs: Optional parameters.
        :return: Title for the view.
        :rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def get_menu_title(cls, **kwargs):
        """
        Return menu entry title for the view.

        Default implementation returns the return value of :py:func:`mydojo.base.BaseView.get_view_title`
        method by default.

        :param dict kwargs: Optional parameters.
        :return: Menu entry title for the view.
        :rtype: str
        """
        return cls.get_view_title(**kwargs)

    @classmethod
    def get_menu_legend(cls, **kwargs):
        """
        Return menu entry legend for the view (menu entry hover tooltip).

        Default implementation returns the return value of :py:func:`mydojo.base.BaseView.get_menu_title`
        method by default.

        :param dict kwargs: Optional parameters.
        :return: Menu entry legend for the view.
        :rtype: str
        """
        return cls.get_menu_title(**kwargs)

    #---------------------------------------------------------------------------

    @property
    def logger(self):
        """
        Return current application`s logger object.
        """
        return flask.current_app.logger


class DecoratedView():
    """
    Wrapper class for classical decorated view functions.
    """
    def __init__(self, view_function):
        self.view_function = view_function

    def get_view_name(self):
        """Simple adapter method to enable support of classical decorated views."""
        return self.view_function.__name__

    def get_view_endpoint(self):
        """Simple adapter method to enable support of classical decorated views."""
        return self.get_view_name()

    def get_view_icon(self):
        """Simple adapter method to enable support of classical decorated views."""
        return 'view-{}'.format(self.get_view_name())


class FileNameView(BaseView):
    """
    Base class for direct file access views. These views can be used to access
    and serve files from arbitrary filesystem directories (that are accessible to
    application process). This can be very usefull for serving files like charts,
    that are periodically generated into configurable and changeable location.
    """

    @classmethod
    def get_directory_path(cls):
        """
        Return absolute path to the directory, that will be used as a base path
        for serving files.

        *This method does not have any default implementation and must be overridden
        by a subclass.*

        :return: Absolute path to the directory for serving files.
        :rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def validate_filename(cls, filename):
        """
        Validate given file name to prevent user from accessing restricted files.

        In default implementation all files pass the validation.

        :param str filename: Name of the file to be validated/filtered.
        :return: ``True`` in case file name is allowed, ``False`` otherwise.
        :rtype: bool
        """
        return bool(filename)

    def dispatch_request(self, filename):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        if not self.validate_filename(filename):
            flask.abort(400)

        self.logger.info(
            "Serving file '{}' from directory '{}'.".format(
                filename,
                self.get_directory_path()
            )
        )
        return flask.send_from_directory(
            self.get_directory_path(),
            filename,
            as_attachment = True
        )


class FileIDView(BaseView):
    """
    Base class for indirrect file access views. These views can be used to access
    and serve files from arbitrary filesystem directories (that are accessible to
    application process). This can be very usefull for serving files like charts,
    that are periodically generated into configurable and changeable location.
    The difference between this view class and :py:class:`FileNameView` is,
    that is this case some kind of identifier is used to access the file and
    provided class method is responsible for translating this identifier into
    real file name.
    """

    @classmethod
    def get_directory_path(cls, fileid, filetype):
        """
        This method must return absolute path to the directory, that will be
        used as a base path for serving files. Parameter ``fileid`` may be used
        internally to further customize the base directory, for example when
        serving some files places into subdirectories based on some part of the
        file name (for example to reduce total number of files in base directory).

        *This method does not have any default implementation and must be overridden
        by a subclass.*

        :param str fileid: Identifier of the requested file.
        :param str filetype: Type of the requested file.
        :return: Absolute path to the directory for serving files.
        :rtype: str
        """
        raise NotImplementedError()

    @classmethod
    def get_filename(cls, fileid, filetype):
        """
        This method must return actual name of the file based on given identifier
        and type.

        *This method does not have any default implementation and must be overridden
        by a subclass.*

        :param str fileid: Identifier of the requested file.
        :param str filetype: Type of the requested file.
        :return: Translated name of the file.
        :rtype: str
        """
        raise NotImplementedError()

    def dispatch_request(self, fileid, filetype):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        basedirpath = self.get_directory_path(fileid, filetype)
        filename = self.get_filename(fileid, filetype)
        if not basedirpath or not filename:
            flask.abort(400)

        self.logger.info(
            "Serving file '{}' from directory '{}'.".format(
                filename,
                basedirpath
            )
        )
        return flask.send_from_directory(
            basedirpath,
            filename,
            as_attachment = True
        )


class RenderableView(BaseView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for all views, that are rendering content based on Jinja2 templates
    or returning JSON/XML data.
    """

    def __init__(self):
        self.response_context = {}

    def mark_time(self, ident, tag = 'default', label = 'Time mark', log = False):
        """
        Mark current time with given identifier and label for further analysis.
        This method can be usefull for measuring durations of various operations.
        """
        mark = [datetime.datetime.utcnow(), ident, tag, label]
        marks = self.response_context.setdefault('time_marks', [])
        marks.append(mark)

        if log:
            if len(marks) <= 1:
                self.logger.info(
                    'Mark {}:{} ({})'.format(*mark[1:])
                )
            else:
                self.logger.info(
                    'Mark {}:{} ({});delta={};delta0={}'.format(
                        *mark[1:],
                        (marks[-1][0]-marks[-2][0]).__str__(), # Time delta from last mark.
                        (marks[-1][0]-marks[0][0]).__str__()   # Time delta from first mark.
                    )
                )

    @classmethod
    def get_view_template(cls):
        """
        Return Jinja2 template file that should be used for rendering the view
        content. This default implementation works only in case the view class
        was properly registered into the parent blueprint/module with
        :py:func:`mydojo.base.MydojOblueprint.register_view_class` method.

        :return: Jinja2 template file to use to render the view.
        :rtype: str
        """
        if cls.module_name:
            return '{}/{}.html'.format(
                cls.module_name,
                cls.get_view_name()
            )
        raise RuntimeError("Unable to guess default view template, because module name was not yet set.")

    def do_before_response(self, **kwargs):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        This method will be called just before generating the response. By providing
        some meaningfull implementation you can use it for some simple item and
        response context mangling tasks.

        :param kwargs: Custom additional arguments.
        """

    def generate_response(self):
        """
        Generate the appropriate response from given response context.

        :param dict response_context: Response context as a dictionary
        """
        raise NotImplementedError()

    @staticmethod
    def abort(status_code, message = None):
        """
        Abort request processing with HTTP status code.
        """
        raise NotImplementedError()

    def flash(self, message, level = 'info'):
        """
        Flash information to the user.
        """
        raise NotImplementedError()

    def redirect(self, default_url = None, exclude_url = None):
        """
        Redirect user to different location.
        """
        raise NotImplementedError()


class SimpleView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for simple views. These are the most, well, simple views, that are
    rendering single template file or directly returning some JSON/XML data without
    any user parameters.

    In most use cases, it should be enough to just enhance the default implementation
    of :py:func:`mydojo.base.RenderableView.get_response_context` to inject
    some additional variables into the template.
    """

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        self.do_before_response()
        return self.generate_response()


class ItemSearchView(RenderableView):
    """
    Base class for item search views.
    """
    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'search'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'action-search'

    @staticmethod
    def get_search_form(request_args):
        """
        Must return instance of :py:mod:`flask_wtf.FlaskForm` appropriate for
        searching given type of items.
        """
        raise NotImplementedError()

    @staticmethod
    def get_query_parameters(form, request_args):
        """
        Get query parameters by comparing contents of processed form data and
        original request arguments. Result of this method can be used for generating
        modified URLs back to current request. One of the use cases is the result
        pager/paginator.
        """
        params = {}
        for arg in request_args:
            if getattr(form, arg, None) and arg in request_args:
                # Handle multivalue request arguments separately
                # Resources:
                #   http://flask.pocoo.org/docs/1.0/api/#flask.Request.args
                #   http://werkzeug.pocoo.org/docs/0.14/datastructures/#werkzeug.datastructures.MultiDict
                try:
                    if form.is_multivalue(arg):
                        params[arg] = request_args.getlist(arg)
                    else:
                        params[arg] = request_args[arg]
                except AttributeError:
                    params[arg] = request_args[arg]
        return params

    def search(self, form_args):
        """
        Perform actual search with given query.
        """
        raise NotImplementedError()

    #---------------------------------------------------------------------------

    def do_before_search(self, form_data):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        This hook method will be called before search attempt.
        """

    def do_after_search(self, items):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        This hook method will be called after successfull search.
        """

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.
        """
        form = self.get_search_form(flask.request.args)
        flask.g.search_form = form

        if mydojo.const.FORM_ACTION_SUBMIT in flask.request.args:
            if form.validate():
                form_data = form.data

                self.mark_time(
                    'preprocess_begin',
                    tag = 'search',
                    label = 'Begin preprocessing for {}'.format(flask.request.full_path),
                    log = True
                )
                self.do_before_search(form_data)
                self.mark_time(
                    'preprocess_end',
                    tag = 'search',
                    label = 'Done preprocessing for {}'.format(flask.request.full_path),
                    log = True
                )

                self.mark_time(
                    'search_begin',
                    tag = 'search',
                    label = 'Begin searching for {}'.format(flask.request.full_path),
                    log = True
                )
                items = self.search(form_data)
                self.mark_time(
                    'search_end',
                    tag = 'search',
                    label = 'Done searching for {}, found: {}'.format(flask.request.full_path, len(items)),
                    log = True
                )
                self.response_context.update(
                    searched = True,
                    items = items,
                    items_count = len(items),
                    form_data = form_data
                )

                self.mark_time(
                    'postprocess_begin',
                    tag = 'search',
                    label = 'Begin postprocessing for {}'.format(flask.request.full_path),
                    log = True
                )
                self.do_after_search(items)
                self.mark_time(
                    'postprocess_end',
                    tag = 'search',
                    label = 'Done postprocessing for {}'.format(flask.request.full_path),
                    log = True
                )
            else:
                self.response_context.update(
                    form_errors = [(field_name, err) for field_name, error_messages in form.errors.items() for err in error_messages]
                )

        self.response_context.update(
            query_params = self.get_query_parameters(form, flask.request.args)
        )
        self.do_before_response()
        return self.generate_response()


class ItemListView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *list* views. These views provide quick and simple access
    to lists of all objects.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'list'

    @classmethod
    def get_action_menu(cls):
        """
        Get action menu for all listed items.
        """
        return None

    @classmethod
    def get_context_action_menu(cls):
        """
        Get context action menu for single particular item.
        """
        return None

    def search(self, form_args):
        """
        Perform actual search with given form arguments.
        """
        raise NotImplementedError()

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        List of all items will be retrieved from database and injected into template
        to be displayed to the user.
        """
        items = self.search({})

        self.response_context.update(
            items = items
        )

        self.do_before_response()
        return self.generate_response()


class ItemShowView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *show* views. These views expect unique item identifier
    as parameter and are supposed to display specific information about single
    item.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'show'

    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_icon`."""
        return 'action-show'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return gettext('Show')

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_url`."""
        return flask.url_for(
            cls.get_view_endpoint(),
            item_id = kwargs['item'].get_id()
        )

    @classmethod
    def authorize_item_action(cls, item):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform access authorization for current user to particular item.
        """
        return True

    @classmethod
    def get_action_menu(cls):
        """
        Get action menu for particular item.
        """
        return None

    def fetch(self, item_id, fetch_by = None):
        """
        Fetch item with given ID.
        """
        raise NotImplementedError()

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        Single item with given unique identifier will be retrieved from database
        and injected into template to be displayed to the user.
        """
        item = self.fetch(item_id)
        if not item:
            self.abort(404)

        if not self.authorize_item_action(item):
            self.abort(403)

        self.response_context.update(
            item_id = item_id,
            item = item
        )

        self.do_before_response()
        return self.generate_response()


class ItemActionView(RenderableView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item action views. These views perform various actions
    (create/update/delete) with given item class.
    """
    @classmethod
    def get_view_icon(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_icon`."""
        return 'action-{}'.format(
            cls.get_view_name().replace('_', '-')
        )

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_url`."""
        return flask.url_for(
            cls.get_view_endpoint(),
            item_id = kwargs['item'].get_id()
        )

    @classmethod
    def get_view_template(cls):
        """*Implementation* of :py:func:`mydojo.base.RenderableView.get_view_template`."""
        return 'form_{}.html'.format(
            cls.get_view_name().replace('-', '_')
        )

    @staticmethod
    def get_message_success(**kwargs):
        """
        *Hook method*. Must return text for flash message in case of action *success*.
        The text may contain HTML characters and will be passed to :py:class:`flask.Markup`
        before being used, so to certain extend you may emphasize and customize the output.
        """
        raise NotImplementedError()

    @staticmethod
    def get_message_failure(**kwargs):
        """
        *Hook method*. Must return text for flash message in case of action *failure*.
        The text may contain HTML characters and will be passed to :py:class:`flask.Markup`
        before being used, so to certain extend you may emphasize and customize the output.
        """
        raise NotImplementedError()

    @staticmethod
    def get_message_cancel(**kwargs):
        """
        *Hook method*. Must return text for flash message in case of action *cancel*.
        The text may contain HTML characters and will be passed to :py:class:`flask.Markup`
        before being used, so to certain extend you may emphasize and customize the output.
        """
        raise NotImplementedError()

    def get_url_next(self):
        """
        *Hook method*. Must return URL for redirection after action *success*. In
        most cases there should be call for :py:func:`flask.url_for` function
        somewhere in this method.
        """
        try:
            return flask.url_for(
                '{}.{}'.format(self.module_name, 'list')
            )
        except werkzeug.routing.BuildError:
            return flask.url_for(
                flask.current_app.config['MYDOJO_ENDPOINT_HOME']
            )

    def check_action_cancel(self, form, **kwargs):
        """
        Check the form for *cancel* button press and cancel the action.
        """
        if getattr(form, mydojo.const.FORM_ACTION_CANCEL).data:
            self.flash(
                flask.Markup(self.get_message_cancel(**kwargs)),
                mydojo.const.FLASH_INFO
            )
            return self.redirect(
                default_url = self.get_url_next()
            )

        return None

    def do_before_action(self, item):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        Will be called before any action handling tasks.
        """

    def do_after_action(self, item):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        Will be called after successfull action handling tasks.
        """

    @classmethod
    def authorize_item_action(cls, item = None):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform access authorization for current user to particular item.
        """
        return True

    @property
    def dbsession(self):
        """
        This property contains the reference to current *SQLAlchemy* database session.
        """
        raise NotImplementedError()

    @property
    def dbmodel(self):
        """
        This property must be implemented in each subclass to
        return reference to appropriate model class based on *SQLAlchemy* declarative
        base.
        """
        raise NotImplementedError()

    def fetch(self, item_id, fetch_by = None):
        """
        Perform actual search with given query.
        """
        raise NotImplementedError()


class ItemCreateView(ItemActionView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *create* action views. These views create new items in
    database.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'create'

    @classmethod
    def get_view_template(cls):
        """
        Return Jinja2 template file that should be used for rendering the view
        content. This default implementation works only in case the view class
        was properly registered into the parent blueprint/module with
        :py:func:`mydojo.base.MyDojoBlueprint.register_view_class` method.

        :return: Title for the view.
        :rtype: str
        """
        if cls.module_name:
            return '{}/creatupdate.html'.format(cls.module_name)
        raise RuntimeError("Unable to guess default view template, because module name was not yet set.")

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return gettext('Create')

    @classmethod
    def get_view_url(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_url`."""
        return flask.url_for(cls.get_view_endpoint())

    @staticmethod
    def get_item_form():
        """
        *Hook method*. Must return instance of :py:mod:`flask_wtf.FlaskForm`
        appropriate for given item class.
        """
        raise NotImplementedError()

    def dispatch_request(self):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form and create new
        instance of appropriate item from form data and finally store the item
        into the database.
        """
        if not self.authorize_item_action():
            self.abort(403)

        item = self.dbmodel()

        form = self.get_item_form()

        cancel_response = self.check_action_cancel(form)
        if cancel_response:
            return cancel_response

        if form.validate_on_submit():
            form_data = form.data
            form.populate_obj(item)

            self.do_before_action(item)

            if form_data[mydojo.const.FORM_ACTION_SUBMIT]:
                try:
                    self.dbsession.add(item)
                    self.dbsession.commit()
                    self.do_after_action(item)

                    self.flash(
                        flask.Markup(self.get_message_success(item = item)),
                        mydojo.const.FLASH_SUCCESS
                    )
                    return self.redirect(default_url = self.get_url_next())

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    self.dbsession.rollback()
                    self.flash(
                        flask.Markup(self.get_message_failure()),
                        mydojo.const.FLASH_FAILURE
                    )
                    flask.current_app.log_exception_with_label(
                        traceback.TracebackException(*sys.exc_info()),
                        self.get_message_failure()
                    )
                    return self.redirect(default_url = self.get_url_next())

        self.response_context.update(
            action_name = gettext('Create'),
            form_url    = flask.url_for(self.get_view_endpoint()),
            form        = form,
            item_action = mydojo.const.ACTION_ITEM_CREATE,
            item        = item
        )

        self.do_before_response()
        return self.generate_response()


class ItemUpdateView(ItemActionView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *update* action views. These views update existing items
    in database.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'update'

    @classmethod
    def get_view_template(cls):
        """
        Return Jinja2 template file that should be used for rendering the view
        content. This default implementation works only in case the view class
        was properly registered into the parent blueprint/module with
        :py:func:`mydojo.base.MyDojoBlueprint.register_view_class` method.

        :return: Title for the view.
        :rtype: str
        """
        if cls.module_name:
            return '{}/creatupdate.html'.format(cls.module_name)
        raise RuntimeError("Unable to guess default view template, because module name was not yet set.")

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return gettext('Update')

    @staticmethod
    def get_item_form(item):
        """
        *Hook method*. Must return instance of :py:mod:`flask_wtf.FlaskForm`
        appropriate for given item class.
        """
        raise NotImplementedError()

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form and update the
        instance of appropriate item from form data and finally store the item
        back into the database.
        """
        item = self.fetch(item_id)
        if not item:
            self.abort(404)

        if not self.authorize_item_action(item):
            self.abort(403)

        self.dbsession.add(item)

        form = self.get_item_form(item)

        cancel_response = self.check_action_cancel(form, item = item)
        if cancel_response:
            return cancel_response

        if form.validate_on_submit():
            form_data = form.data
            form.populate_obj(item)

            self.do_before_action(item)

            if form_data[mydojo.const.FORM_ACTION_SUBMIT]:
                try:
                    if item not in self.dbsession.dirty:
                        self.flash(
                            gettext('No changes detected, no update needed.'),
                            mydojo.const.FLASH_INFO
                        )
                        return self.redirect(default_url = self.get_url_next())

                    self.dbsession.commit()
                    self.do_after_action(item)

                    self.flash(
                        flask.Markup(self.get_message_success(item = item)),
                        mydojo.const.FLASH_SUCCESS
                    )
                    return self.redirect(default_url = self.get_url_next())

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    self.dbsession.rollback()
                    self.flash(
                        flask.Markup(self.get_message_failure(item = item)),
                        mydojo.const.FLASH_FAILURE
                    )
                    flask.current_app.log_exception_with_label(
                        traceback.TracebackException(*sys.exc_info()),
                        self.get_message_failure(item = item)
                    )
                    return self.redirect(default_url = self.get_url_next())

        self.response_context.update(
            action_name = gettext('Update'),
            form_url    = flask.url_for(self.get_view_endpoint(), item_id = item_id),
            form        = form,
            item_action = mydojo.const.ACTION_ITEM_UPDATE,
            item_id     = item_id,
            item        = item
        )

        self.do_before_response()
        return self.generate_response()


class ItemDeleteView(ItemActionView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item *delete* action views. These views delete existing items
    from database.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'delete'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return gettext('Delete')

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form and delete the
        instance of appropriate item from database in case user agreed to the
        item removal action.
        """
        item = self.fetch(item_id)
        if not item:
            self.abort(404)

        if not self.authorize_item_action(item):
            self.abort(403)

        form = ItemActionConfirmForm()

        cancel_response = self.check_action_cancel(form, item = item)
        if cancel_response:
            return cancel_response

        if form.validate_on_submit():
            form_data = form.data

            self.do_before_action(item)

            if form_data[mydojo.const.FORM_ACTION_SUBMIT]:
                try:
                    self.dbsession.delete(item)
                    self.dbsession.commit()
                    self.do_after_action(item)

                    self.flash(
                        flask.Markup(self.get_message_success(item = item)),
                        mydojo.const.FLASH_SUCCESS
                    )
                    return self.redirect(
                        default_url = self.get_url_next(),
                        exclude_url = flask.url_for(
                            '{}.{}'.format(self.module_name, 'show'),
                            item_id = item.id
                        )
                    )

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    self.dbsession.rollback()
                    self.flash(
                        flask.Markup(self.get_message_failure(item = item)),
                        mydojo.const.FLASH_FAILURE
                    )
                    flask.current_app.log_exception_with_label(
                        traceback.TracebackException(*sys.exc_info()),
                        self.get_message_failure(item = item)
                    )
                    return self.redirect(default_url = self.get_url_next())

        self.response_context.update(
            confirm_form = form,
            confirm_url  = flask.url_for(self.get_view_endpoint(), item_id = item_id),
            item_name    = str(item),
            item_id      = item_id,
            item         = item
        )

        self.do_before_response()
        return self.generate_response()


class ItemChangeView(ItemActionView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for single item change views, that are doing some simple modification
    of item attribute, like enable/disable item, etc.
    """

    @classmethod
    def validate_item_change(cls, item):  # pylint: disable=locally-disabled,unused-argument
        """
        Perform validation of particular change to given item.
        """
        return True

    @classmethod
    def change_item(cls, item):
        """
        *Hook method*: Change given item in any desired way.

        :param item: Item to be changed/modified.
        """
        raise NotImplementedError()

    def dispatch_request(self, item_id):  # pylint: disable=locally-disabled,arguments-differ
        """
        Mandatory interface required by the :py:func:`flask.views.View.dispatch_request`.
        Will be called by the **Flask** framework to service the request.

        This method will attempt to validate the submitted form, then perform
        arbitrary mangling action with the item and submit the changes to the
        database.
        """
        item = self.fetch(item_id)
        if not item:
            self.abort(404)

        if not self.authorize_item_action(item):
            self.abort(403)

        if not self.validate_item_change(item):
            self.abort(400)

        form = ItemActionConfirmForm()

        cancel_response = self.check_action_cancel(form, item = item)
        if cancel_response:
            return cancel_response

        if form.validate_on_submit():
            form_data = form.data

            self.do_before_action(item)

            if form_data[mydojo.const.FORM_ACTION_SUBMIT]:
                try:
                    self.change_item(item)
                    if item not in self.dbsession.dirty:
                        self.flash(
                            gettext('No changes detected, no update needed.'),
                            mydojo.const.FLASH_INFO
                        )
                        return self.redirect(default_url = self.get_url_next())

                    self.dbsession.commit()
                    self.do_after_action(item)

                    self.flash(
                        flask.Markup(self.get_message_success(item = item)),
                        mydojo.const.FLASH_SUCCESS
                    )
                    try:
                        exclude_url = flask.url_for(
                            '{}.{}'.format(self.module_name, 'show'),
                            item_id = item.id
                        )
                    except werkzeug.routing.BuildError:
                        exclude_url = None
                    return self.redirect(
                        default_url = self.get_url_next(),
                        exclude_url = exclude_url
                    )

                except Exception:  # pylint: disable=locally-disabled,broad-except
                    self.dbsession.rollback()
                    self.flash(
                        flask.Markup(self.get_message_failure(item = item)),
                        mydojo.const.FLASH_FAILURE
                    )
                    flask.current_app.log_exception_with_label(
                        traceback.TracebackException(*sys.exc_info()),
                        self.get_message_failure(item = item)
                    )
                    return self.redirect(default_url = self.get_url_next())

        self.response_context.update(
            confirm_form = form,
            confirm_url  = flask.url_for(self.get_view_endpoint(), item_id = item_id),
            item_name    = str(item),
            item_id      = item_id,
            item         = item
        )

        self.do_before_response()
        return self.generate_response()


class ItemDisableView(ItemChangeView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item disabling views.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'disable'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return gettext('Disable')

    @classmethod
    def validate_item_change(cls, item):  # pylint: disable=locally-disabled,unused-argument
        """*Implementation* of :py:func:`mydojo.base.ItemChangeView.validate_item_change`."""
        # Reject item change in case given item is already disabled.
        if not item.enabled:
            return False
        return True

    @classmethod
    def change_item(cls, item):
        """*Implementation* of :py:func:`mydojo.base.ItemChangeView.change_item`."""
        item.enabled = False


class ItemEnableView(ItemChangeView):  # pylint: disable=locally-disabled,abstract-method
    """
    Base class for item enabling views.
    """

    @classmethod
    def get_view_name(cls):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_view_name`."""
        return 'enable'

    @classmethod
    def get_view_title(cls, **kwargs):
        """*Implementation* of :py:func:`mydojo.base.BaseView.get_menu_title`."""
        return gettext('Enable')

    @classmethod
    def validate_item_change(cls, item):  # pylint: disable=locally-disabled,unused-argument
        """*Implementation* of :py:func:`mydojo.base.ItemChangeView.validate_item_change`."""
        # Reject item change in case given item is already enabled.
        if item.enabled:
            return False
        return True

    @classmethod
    def change_item(cls, item):
        """*Implementation* of :py:func:`mydojo.base.ItemChangeView.change_item`."""
        item.enabled = True
