#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains menu model for MyDojo application.
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import re
import collections

#
# Flask related modules.
#
import flask
import flask_login
import flask_principal

#
# Custom modules.
#
import mydojo.const
import mydojo.auth

CRE_STRIP_QUESTION = re.compile(r'\?$')

ENTRY_SUBMENU   = 'submenu'
ENTRY_SUBMENUDB = 'submenu_db'
ENTRY_VIEW      = 'view'
ENTRY_ENDPOINT  = 'endpoint'
ENTRY_LINK      = 'link'
ENTRY_TEST      = 'test'


def _url_segments(path):
    parts = path.split('/')[1:]
    if parts and parts[-1] == '':
        parts.pop()
    return parts

def _is_active(this_url, request):
    request_path      = request.script_root + request.path
    request_path_full = request.script_root + request.full_path
    # For some reason in certain cases the '?' is appended to the end of request
    # path event in case there are no additional parameters. Get rid of that.
    request_path_full = CRE_STRIP_QUESTION.sub('', request_path_full)
    if len(this_url) > 1:
        segments_url = _url_segments(this_url)
        segments_request = _url_segments(request_path)
        matching_segments = segments_request == segments_url
    else:
        matching_segments = False
    matching_completpath = request_path_full == this_url
    return matching_segments or matching_completpath


def _filter_menu_entries(entries, **kwargs):
    """
    *Helper function*. Filter given list of menu entries for current user. During
    the filtering following operations will be performed:

    * Remove all entries accessible only for authenticated users, when the current
      user is not authenticated.
    * Remove all entries for which the current user has not sufficient permissions.
    * Remove all empty submenu entries.

    :param collections.OrderedDict entries: List of menu entries.
    :param item: Optional item for which the menu should be parametrized.
    :return: Filtered list of menu entries.
    :rtype: collections.OrderedDict
    """
    result = collections.OrderedDict()
    for entry_id, entry in entries.items():
        #print("Processing menu entry '{}'.".format(entry_id))

        # Filter out entries protected with authentication.
        if entry.authentication:
            if not flask_login.current_user.is_authenticated:
                #print("Hiding menu entry '{}', accessible only to authenticated users.".format(entry_id))
                continue

        # Filter out entries protected with authorization.
        if entry.authorization:
            hideflag = False
            for authspec in entry.authorization:
                # Authorization rules may be specified as instances of flask_principal.Permission.
                if isinstance(authspec, flask_principal.Permission):
                    if not authspec.can():
                        #print("Hiding menu entry '{}', accessible only to '{}'.".format(entry_id, str(authspec)))
                        hideflag = True
                # Authorization rules may be specified as indices to hawat.acl permission dictionary.
                else:
                    if not mydojo.auth.PERMISSIONS[authspec].can():
                        #print("Hiding menu entry '{}', accessible only to '{}'.".format(entry_id, str(authspec)))
                        hideflag = True
            if hideflag:
                continue

        if entry.type == ENTRY_SUBMENU:
            # Filter out empty submenus.
            if not _filter_menu_entries(entry._entries, **kwargs):  # pylint: disable=locally-disabled,protected-access
                #print("Hiding menu entry '{}', empty submenu.".format(entry_id))
                continue

        if entry.type == ENTRY_VIEW:
            # Check item action authorization callback, if exists.
            if hasattr(entry.view, 'authorize_item_action'):
                params = entry._pick_params(kwargs)  # pylint: disable=locally-disabled,protected-access
                if not entry.view.authorize_item_action(**params):
                    #print("Hiding menu entry '{}', inaccessible item action for item '{}'.".format(entry_id, str(item)))
                    continue

            # Check item change validation callback, if exists.
            if hasattr(entry.view, 'validate_item_change'):
                params = entry._pick_params(kwargs)  # pylint: disable=locally-disabled,protected-access
                if not entry.view.validate_item_change(**params):
                    #print("Hiding menu entry '{}', invalid item change for item '{}'.".format(entry_id, str(item)))
                    continue

        result[entry_id] = entry

    return result

def _get_menu_entries(entries, **kwargs):
    """
    *Helper function*. Return filtered and sorted menu entries for current user.

    :param collections.OrderedDict entries: List of menu entries.
    :param item: Optional item for which the menu should be parametrized.
    :return: Filtered list of menu entries.
    :rtype: collections.OrderedDict
    """
    return sorted(
        list(
            _filter_menu_entries(entries, **kwargs).values()
        ),
        key = lambda x: x.position

    )


#-------------------------------------------------------------------------------


class MenuEntry:  # pylint: disable=locally-disabled,too-many-instance-attributes
    """
    Base class for all menu entries.
    """
    def __init__(self, ident, **kwargs):
        self.type       = None
        self.ident      = ident
        self.position   = kwargs.get('position', 0)
        self._icon      = kwargs.get('icon', None)
        self._title     = kwargs.get('title', None)
        self._legend    = kwargs.get('legend', None)
        self._params    = kwargs.get('params', None)
        self.hideicon   = kwargs.get('hideicon', False)
        self.hidetitle  = kwargs.get('hidetitle', False)
        self.hidelegend = kwargs.get('hidelegend', False)
        self.resptitle  = kwargs.get('resptitle', False)
        self.respicon   = kwargs.get('respicon', False)
        self.resplegend = kwargs.get('resplegend', False)

    def __repr__(self):
        return '{}<type={},ident={}>'.format(
            self.__class__.__name__,
            self.type,
            self.ident
        )

    def _pick_params(self, params):
        params = self._params or params or {}
        try:
            return params()
        except TypeError:
            return params

    def get_icon(self, **kwargs):
        """
        Return icon for current menu entry.

        :param dict kwargs: Optional menu entry parameters.
        :return: Icon for current menu entry.
        :rtype: str
        """
        if self._icon and not self.hideicon:
            try:
                return self._icon(**self._pick_params(kwargs))
            except TypeError:
                return self._icon
        return None

    def get_title(self, **kwargs):
        """
        Return title for current menu entry.

        :param dict kwargs: Optional menu entry parameters.
        :return: Title for current menu entry.
        :rtype: str
        """
        if self._title and not self.hidetitle:
            try:
                return self._title(**self._pick_params(kwargs))
            except TypeError:
                return self._title
        return None

    def get_legend(self, **kwargs):
        """
        Return legend for current menu entry.

        :param dict kwargs: Optional menu entry parameters.
        :return: Legend for current menu entry.
        :rtype: str
        """
        if self._legend and not self.hidelegend:
            try:
                return self._legend(**self._pick_params(kwargs))
            except TypeError:
                return self._legend
        return None

    def get_entries(self, **kwargs):
        """
        Get list of sub-entries for this menu entry.

        :param dict kwargs: Optional menu entry parameters.
        :return: List of submenu entries for this entry.
        :rtype: list
        """
        raise NotImplementedError()

    def add_entry(self, ident, subentry):
        """
        Add new entry into the submenu of this menu entry.

        :param str ident: Unique identifier of the subentry within the submenu.
        """
        raise NotImplementedError()

    def is_active(self, request, **kwargs):
        """
        Check, if this menu entry is active thanks to the given request.

        :param flask.Request request: Current request object.
        :param dict kwargs: Optional menu entry parameters.
        :return: ``True`` in case menu entry is active, ``False`` otherwise.
        :rtype: bool
        """
        raise NotImplementedError()


class SubmenuEntry(MenuEntry):  # pylint: disable=locally-disabled,too-many-instance-attributes
    """
    Class for entries representing whole submenu trees.
    """

    def __init__(self, ident, **kwargs):
        super().__init__(ident, **kwargs)
        self.type             = ENTRY_SUBMENU
        self.flat_group       = kwargs.get('flat_group', False)
        self.separator_before = kwargs.get('separator_before', False)
        self.separator_after  = kwargs.get('separator_after', False)
        self.align_right      = kwargs.get('align_right', False)
        self.authentication   = kwargs.get('authentication', False)
        self.authorization    = kwargs.get('authorization', [])
        self._entries         = collections.OrderedDict()

    def get_entries(self, **kwargs):
        return _get_menu_entries(
            self._entries,
            **self._pick_params(kwargs)
        )

    def add_entry(self, ident, subentry):
        # Split ident on '.' character.
        path = ident.split('.', 1)
        # Last chunk, append to self.
        if len(path) == 1:
            self._entries[path[0]] = subentry
        # Delegate to sub-submenu
        else:
            self._entries[path[0]].add_entry(path[1], subentry)

    def is_active(self, request, **kwargs):
        return False


class DBSubmenuEntry(SubmenuEntry):
    """
    Class for entries representing whole submenu trees whose contents are fetched
    on demand from database.
    """

    def __init__(self, ident, **kwargs):
        super().__init__(ident, **kwargs)
        self._entry_fetcher = kwargs['entry_fetcher']
        self._entry_builder = kwargs['entry_builder']

    def _fetch_entries(self):
        entries = collections.OrderedDict()
        items = self._entry_fetcher()
        if items:
            for i in items:
                entry_id = '{}'.format(str(i))
                entries[entry_id] = self._entry_builder(entry_id, i)
        return entries

    def get_entries(self, **kwargs):
        return _get_menu_entries(
            self._fetch_entries,
            **self._pick_params(kwargs)
        )

    def add_entry(self, ident, subentry):
        raise RuntimeError(
            "Unable to append entry '{}' to '{}' DB submenu entry.".format(
                repr(subentry),
                self.ident
            )
        )


class ViewEntry(MenuEntry):
    """
    Class representing menu entries pointing to application views.
    """

    def __init__(self, ident, **kwargs):
        super().__init__(ident, **kwargs)
        self.type = ENTRY_VIEW
        self.view = kwargs['view']
        self._url = kwargs.get('url', None)

    @property
    def endpoint(self):
        """
        Property containing routing endpoint for current entry.

        :return: Routing endpoint for current menu entry.
        :rtype: str
        """
        return self.view.get_view_endpoint()

    @property
    def authentication(self):
        """
        Property containing authentication information for current entry.

        :return: Authentication information for current menu entry.
        :rtype: str
        """
        return self.view.authentication

    @property
    def authorization(self):
        """
        Property containing authorization information for current entry.

        :return: Authorization information for current menu entry.
        :rtype: str
        """
        return self.view.authorization

    def get_icon(self, **kwargs):
        params = self._pick_params(kwargs)
        if not self.hideicon:
            value = self._icon or self.view.get_view_icon()
            if value:
                try:
                    return value(**params)
                except TypeError:
                    return value
        return mydojo.const.ICON_NAME_MISSING_ICON

    def get_title(self, **kwargs):
        params = self._pick_params(kwargs)
        if not self.hidetitle:
            value = self._title or self.view.get_menu_title(**params)
            if value:
                try:
                    return value(**params)
                except TypeError:
                    return value
        return None

    def get_legend(self, **kwargs):
        params = self._pick_params(kwargs)
        if not self.hidelegend:
            value = self._legend or self.view.get_menu_legend(**params)
            if value:
                try:
                    return value(**params)
                except TypeError:
                    return value
        return None

    def get_url(self, **kwargs):
        """
        Return URL for current menu entry.

        :param dict kwargs: Optional menu entry parameters.
        :return: URL for current menu entry.
        :rtype: str
        """
        params = self._pick_params(kwargs)
        value = self._url or self.view.get_view_url(**params)
        if value:
            try:
                return value(**params)
            except TypeError:
                return value
        return flask.url_for(self.endpoint)

    def get_entries(self, **kwargs):
        return []

    def add_entry(self, ident, subentry):
        raise RuntimeError(
            "Unable to append submenu to '{}' view menu entry.".format(
                self.ident
            )
        )

    def is_active(self, request, **kwargs):
        print("Checking if view menu entry '{}' is active.".format(self.ident))
        params = self._pick_params(kwargs)
        return _is_active(
            self.get_url(**params),
            request
        )


class EndpointEntry(ViewEntry):
    """
    Class representing menu entries pointing to application routing endpoints.
    """

    def __init__(self, ident, endpoint, **kwargs):
        kwargs['view'] = flask.current_app.get_endpoint_class(endpoint)
        super().__init__(ident, **kwargs)


class LinkEntry(MenuEntry):
    """
    Class representing menu entries pointing to application views.
    """

    def __init__(self, ident, **kwargs):
        super().__init__(ident, **kwargs)
        self.type           = ENTRY_LINK
        self.authentication = kwargs.get('authentication', False)
        self.authorization  = kwargs.get('authorization', [])
        self._url           = kwargs.get('url')

    def get_url(self, **kwargs):
        """
        Return URL for current menu entry.

        :param dict kwargs: Optional menu entry parameters.
        :return: URL for current menu entry.
        :rtype: str
        """
        params = self._pick_params(kwargs)
        try:
            return self._url(**params)
        except TypeError:
            return self._url

    def get_entries(self, **kwargs):
        return []

    def add_entry(self, ident, subentry):
        raise RuntimeError(
            "Unable to append submenu to '{}' link menu entry.".format(
                self.ident
            )
        )

    def is_active(self, request, **kwargs):
        #print("Checking if link menu entry '{}' is active.".format(self.ident))
        params = self._pick_params(kwargs)
        return _is_active(
            self.get_url(**params),
            request
        )


class TestEntry(MenuEntry):
    """
    Class for menu entries for testing and demonstration purposes.
    """

    def __init__(self, ident, **kwargs):
        super().__init__(ident, **kwargs)
        self.type           = ENTRY_TEST
        self.authentication = kwargs.get('authentication', False)
        self.authorization  = kwargs.get('authorization', [])

    def get_entries(self, **kwargs):
        return []

    def add_entry(self, ident, subentry):
        raise RuntimeError(
            "Unable to append submenu to '{}' test menu entry.".format(
                self.ident
            )
        )

    def is_active(self, request, **kwargs):
        raise RuntimeError(
            "This method makes no sense for test menu entries."
        )


class Menu:
    """
    Class for application menu.
    """
    def __init__(self):
        self._entries = collections.OrderedDict()

    def __repr__(self):
        return '{}'.format(self._entries)

    def get_entries(self, **kwargs):
        """
        Get list of entries for this menu.

        :param item: Optional item for which the menu should be parametrized.
        :return: List of entries for this menu.
        :rtype: list
        """
        return _get_menu_entries(self._entries, **kwargs)

    def add_entry(self, entry_type, ident, **kwargs):
        """
        Add new entry into the menu.

        :param str entry_type: Type/class of the menu entry as string, object of the correct class will be created.
        :param str ident: Unique identifier of the entry within the menu.
        :param dict kwargs: Additional arguments, that will be passed to the constructor of the appropriate entry class.
        """
        entry = None
        if   entry_type == ENTRY_SUBMENU:
            entry = SubmenuEntry(ident, **kwargs)
        elif entry_type == ENTRY_SUBMENUDB:
            entry = DBSubmenuEntry(ident, **kwargs)
        elif entry_type == ENTRY_VIEW:
            entry = ViewEntry(ident, **kwargs)
        elif entry_type == ENTRY_ENDPOINT:
            entry = EndpointEntry(ident, **kwargs)
        elif entry_type == ENTRY_LINK:
            entry = LinkEntry(ident, **kwargs)
        elif entry_type == ENTRY_TEST:
            entry = TestEntry(ident, **kwargs)
        if not entry:
            raise ValueError(
                "Invalid value '{}' for Menu entry type for entry '{}'.".format(
                    entry_type,
                    ident
                )
            )

        path = ident.split('.', 1)
        # Last chunk, append to self.
        if len(path) == 1:
            self._entries[path[0]] = entry
        else:
            self._entries[path[0]].add_entry(path[1], entry)


#
# When executed directly perform some demonstrations.
#
if __name__ == '__main__':

    MENU = Menu()
    MENU.add_entry('test', 'test0', position = 10)
    MENU.add_entry('test', 'test1', position = 10)
    MENU.add_entry('test', 'test2', position = 20)
    MENU.add_entry('test', 'test3', position = 40)
    MENU.add_entry('test', 'test4', position = 30)

    MENU.add_entry('submenu', 'sub1', position = 50)
    MENU.add_entry('submenu', 'sub2', position = 60)

    MENU.add_entry('test', 'sub1.test1', position = 10)
    MENU.add_entry('test', 'sub1.test2', position = 20)
    MENU.add_entry('test', 'sub1.test3', position = 40)
    MENU.add_entry('test', 'sub1.test4', position = 30)
    MENU.add_entry('test', 'sub2.test1', position = 10)
    MENU.add_entry('test', 'sub2.test2', position = 20)
    MENU.add_entry('test', 'sub2.test3', position = 40)
    MENU.add_entry('test', 'sub2.test4', position = 30)

    import pprint

    pprint.pprint(MENU.get_entries())

    pprint.pprint(MENU.__class__)
