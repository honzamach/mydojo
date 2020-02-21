#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains authentication and authorization features for MyDojo application.
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


from functools import partial

import flask_login
import flask_principal

import mydojo.const


LOGIN_MANAGER = flask_login.LoginManager()
PRINCIPAL     = flask_principal.Principal(skip_static = True)


MembershipNeed = partial(flask_principal.Need, 'membership')   # pylint: disable=locally-disabled,invalid-name
MembershipNeed.__doc__ = """A need with the method preset to `"membership"`."""

ManagementNeed = partial(flask_principal.Need, 'management')   # pylint: disable=locally-disabled,invalid-name
ManagementNeed.__doc__ = """A need with the method preset to `"management"`."""


PERMISSION_ADMIN = flask_principal.Permission(
    flask_principal.RoleNeed(mydojo.const.ROLE_ADMIN)
)
"""
The :py:class:`flask_principal.Permission` permission for users with *admin* role
(ultimate power-user with unrestricted access to the whole system).
"""

PERMISSION_DEVELOPER = flask_principal.Permission(
    flask_principal.RoleNeed(mydojo.const.ROLE_DEVELOPER)
)
"""
The :py:class:`flask_principal.Permission` permission for users with *developer* role
(system developers with access to additional development and debugging data output).
"""

PERMISSION_USER = flask_principal.Permission(
    flask_principal.RoleNeed(mydojo.const.ROLE_USER)
)
"""
The :py:class:`flask_principal.Permission` permission for regular users with *user* role.
"""

PERMISSION_ANY = flask_principal.Permission(
    flask_principal.RoleNeed(mydojo.const.ROLE_ADMIN),
    flask_principal.RoleNeed(mydojo.const.ROLE_DEVELOPER),
    flask_principal.RoleNeed(mydojo.const.ROLE_USER)
)
"""
The concatenated :py:class:`flask_principal.Permission` permission for any user role
(*admin*, *maintainer*, *developer* or *user*).
"""

PERMISSIONS = {
    mydojo.const.ROLE_ADMIN:     PERMISSION_ADMIN,
    mydojo.const.ROLE_DEVELOPER: PERMISSION_DEVELOPER,
    mydojo.const.ROLE_USER:      PERMISSION_USER,
    mydojo.const.ROLE_ANY:       PERMISSION_ANY
}
"""
Map for accessing permission objects by name.
"""
