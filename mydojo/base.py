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
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import collections
import datetime
import weakref

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

#
# Custom modules.
#
import mydojo.const
import mydojo.db
import mydojo.menu
import mydojo.errors
from mydojo.forms import get_redirect_target


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

        self.view_classes = {}
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
            self.config.setdefault(
                mydojo.const.CFGKEY_MODULES_LOADED,
                collections.OrderedDict()
            ).setdefault(blueprint.name, blueprint)

            if hasattr(blueprint, 'register_app'):
                blueprint.register_app(self)

            self.view_classes.update(blueprint.view_classes)
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
                    "Invalid blueprint module '{}', does not provide the 'get_blueprint' factory method.".format(name)
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
        return endpoint in self.view_classes

    def get_endpoint_class(self, endpoint, quiet = False):
        """
        Get reference to view class registered to given routing endpoint.

        :param str endpoint: Application routing endpoint.
        :return: Reference to view class.
        :rtype: class
        """
        if not endpoint in self.view_classes:
            if quiet:
                return None
            raise MyDojoAppException(
                "Unknown endpoint name '{}'.".format(endpoint)
            )
        return self.view_classes[endpoint]

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

        self.view_classes = {}
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

        # Store the reference to view class to internal registry, so it can be
        # looked up within the application. This feature can be then used for
        # example for view link authorization (check, that current user has
        # privileges to access the view before generating link).
        self.view_classes[view_class.get_view_endpoint()] = view_class

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
    def search_by(self):
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
        *Hook method*. Modify given query according to the given arguments.
        """
        return query

    def fetch(self, item_id):
        """
        Fetch item with given primary identifier from the database.
        """
        return self.dbquery().filter(self.search_by == item_id).one()

    def fetch_first(self, item_id):
        """
        Fetch item with given primary identifier from the database.
        """
        return self.dbquery().filter(self.search_by == item_id).first()

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
        return flask.url_for(
            cls.get_view_endpoint(),
            **kwargs
        )

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

        Default implementation returns the return value of :py:func:`hawat.base.HawatBaseView.get_menu_title`
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

        Default implementation returns the return value of :py:func:`hawat.base.HawatBaseView.get_view_title`
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

        Default implementation returns the return value of :py:func:`hawat.base.HawatBaseView.get_menu_title`
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
    def get_directory_path(cls, fileid):
        """
        This method must return absolute path to the directory, that will be
        used as a base path for serving files. Parameter ``fileid`` may be used
        internally to further customize the base directory, for example when
        serving some files places into subdirectories based on some part of the
        file name (for example to reduce total number of files in base directory).

        *This method does not have any default implementation and must be overridden
        by a subclass.*

        :param str fileid: Identifier of the requested file.
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
        basedirpath = self.get_directory_path(fileid)
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
