#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains database initializations and models for MyDojo application.
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import datetime
import json

#
# Flask related modules.
#
import sqlalchemy
import sqlalchemy.dialects.postgresql

from sqlalchemy.schema import DropTable
from sqlalchemy.ext.compiler import compiles

import flask_sqlalchemy

#
# Modify compilation of DROP TABLE for PostgreSQL databases to enable CASCADE feature.
# Otherwise it is not possible to delete the database schema with:
#   MODEL.metadata.drop_all(engine)
#
@compiles(DropTable, "postgresql")
def _compile_drop_table(element, compiler, **kwargs):  # pylint: disable=locally-disabled,unused-argument
    return compiler.visit_drop_table(element) + " CASCADE"


SQLDB = flask_sqlalchemy.SQLAlchemy()


class BaseMixin:
    """
    Base class providing usefull mixin functionality.
    """
    id = sqlalchemy.Column(  # pylint: disable=locally-disabled,invalid-name
        sqlalchemy.Integer,
        primary_key = True
    )
    createtime = sqlalchemy.Column(
        sqlalchemy.DateTime,
        default = datetime.datetime.utcnow
    )

    def get_id(self):
        """
        Getter for retrieving current primary ID.
        """
        return self.id

    def to_dict(self):
        """
        Export object into dictionary containing only primitive data types.
        """
        raise NotImplementedError()

    def to_json(self):
        """
        Export object into JSON string.
        """
        return json.dumps(
            self.to_dict(),
            indent = 4,
            sort_keys = True
        )


#-------------------------------------------------------------------------------


_asoc_group_members = sqlalchemy.Table(  # pylint: disable=locally-disabled,invalid-name
    'asoc_group_members',
    SQLDB.Model.metadata,
    sqlalchemy.Column(
        'group_id',
        sqlalchemy.ForeignKey('groups.id'),
        primary_key = True
    ),
    sqlalchemy.Column(
        'user_id',
        sqlalchemy.ForeignKey('users.id'),
        primary_key = True
    )
)
"""
Association table representing user*group relation: group membership.

What users are members of what groups.
"""

_asoc_group_managers = sqlalchemy.Table(  # pylint: disable=locally-disabled,invalid-name
    'asoc_group_managers',
    SQLDB.Model.metadata,
    sqlalchemy.Column(
        'group_id',
        sqlalchemy.ForeignKey('groups.id'),
        primary_key = True
    ),
    sqlalchemy.Column(
        'user_id',
        sqlalchemy.ForeignKey('users.id'),
        primary_key = True
    )
)
"""
Association table representing user*group relation: group management.

What users can manage what groups.
"""


class UserModel(SQLDB.Model, BaseMixin):  # pylint: disable=locally-disabled,too-many-instance-attributes
    """
    Class representing user objects within the SQL database mapped to ``users``
    table.
    """
    __tablename__ = 'users'

    login = sqlalchemy.Column(
        sqlalchemy.String(50),
        unique = True,
        index = True
    )
    fullname = sqlalchemy.Column(
        sqlalchemy.String(100),
        nullable = False
    )
    email = sqlalchemy.Column(
        sqlalchemy.String(250),
        nullable = False
    )
    roles = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.ARRAY(
            sqlalchemy.String(20),
            dimensions = 1
        ),
        nullable = False,
        default = []
    )
    enabled = sqlalchemy.Column(
        sqlalchemy.Boolean,
        nullable = False,
        default = True
    )

    password = sqlalchemy.Column(
        sqlalchemy.String
    )
    apikey = sqlalchemy.Column(
        sqlalchemy.String,
        index = True
    )

    locale = sqlalchemy.Column(
        sqlalchemy.String(20)
    )
    timezone = sqlalchemy.Column(
        sqlalchemy.String(50)
    )

    memberships = sqlalchemy.orm.relationship(
        'GroupModel',
        secondary = _asoc_group_members,
        back_populates = 'members'
    )
    managements = sqlalchemy.orm.relationship(
        'GroupModel',
        secondary = _asoc_group_managers,
        back_populates = 'managers'
    )

    logintime = sqlalchemy.Column(
        sqlalchemy.DateTime
    )

    def __repr__(self):
        return "<User(login='{}', fullname='{}')>".format(self.login, self.fullname)

    def __str__(self):
        return '{}'.format(self.login)

    def to_dict(self):
        """
        *Interface implementation:* Implementation of :py:func:`mydojo.db.BaseMixin.to_dict` method.
        """
        return {
            'id':           int(self.id),
            'createtime':   str(self.createtime),
            'logintime':    str(self.logintime),
            'login':        str(self.login),
            'fullname':     str(self.fullname),
            'email':        str(self.email),
            'roles':        [ str(x) for x in self.roles],
            'enabled':      bool(self.enabled),
            'password':     str(self.pasword),
            'apikey':       str(self.apikey),
            'locale':       str(self.locale),
            'timezone':     str(self.timezone),
            'memberships':  [(x.id, x.name) for x in self.memberships],
            'managements':  [(x.id, x.name) for x in self.managements]
        }

    @classmethod
    def from_dict(cls, structure, defaults = None):
        """
        Convenience method for creating :py:class:`mydojo.db.UserModel` object
        from ``dict`` objects.
        """
        if not defaults:
            defaults = {}

        sqlobj = cls()
        sqlobj.login    = structure.get('login')
        sqlobj.fullname = structure.get('fullname')
        sqlobj.email    = structure.get('email', structure.get('login'))
        sqlobj.roles    = [str(i) for i in structure.get('roles', [])]
        sqlobj.enabled  = structure.get('enabled', None)
        sqlobj.password = structure.get('password', None)
        sqlobj.apikey   = structure.get('apikey', None)
        sqlobj.locale   = structure.get('locale', None)
        sqlobj.timezone = structure.get('timezone', None)

        return sqlobj


class GroupModel(SQLDB.Model, BaseMixin):
    """
    Class representing group objects within the SQL database mapped to ``groups``
    table.
    """
    __tablename__ = 'groups'

    name = sqlalchemy.Column(
        sqlalchemy.String(100),
        unique = True,
        index = True
    )
    description = sqlalchemy.Column(
        sqlalchemy.String
    )
    enabled = sqlalchemy.Column(
        sqlalchemy.Boolean,
        nullable = False,
        default = True
    )

    members = sqlalchemy.orm.relationship(
        'UserModel',
        secondary = _asoc_group_members,
        back_populates = 'memberships'
    )
    managers = sqlalchemy.orm.relationship(
        'UserModel',
        secondary = _asoc_group_managers,
        back_populates = 'managements'
    )

    parent_id = sqlalchemy.Column(
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey('groups.id')
    )
    children = sqlalchemy.orm.relationship(
        'GroupModel',
        backref = sqlalchemy.orm.backref(
            'parent',
            remote_side = 'GroupModel.id'
        )
    )

    def __repr__(self):
        return "<Group(name='{}')>".format(self.name)

    def __str__(self):
        return '{}'.format(self.name)

    def to_dict(self):
        """
        *Interface implementation:* Implementation of :py:func:`mydojo.db.BaseMixin.to_dict` method.
        """
        return {
            'id':          int(self.id),
            'createtime':  str(self.createtime),
            'name':        str(self.name),
            'description': str(self.description),
            'enabled':     bool(self.enabled),
            'members':     [(x.id, x.login) for x in self.members],
            'managers':    [(x.id, x.login) for x in self.managers],
            'parent':      str(self.parent),
        }

    @classmethod
    def from_dict(cls, structure, defaults = None):
        """
        Convenience method for creating :py:class:`mydojo.db.GroupModel` object
        from ``dict`` objects.
        """
        if not defaults:
            defaults = {}

        sqlobj = cls()
        sqlobj.createtime  = structure.get('createtime')
        sqlobj.name        = structure.get('name')
        sqlobj.description = structure.get('description', '-- undisclosed --')

        return sqlobj
