#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains custom commands for ``mydojo-cli`` command line interface.
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import re
import sys
import traceback
import sqlalchemy

import click
from flask.cli import AppGroup

import mydojo.const
import mydojo.db


def validate_email(ctx, param, value):
    if value:
        if mydojo.const.CRE_EMAIL.match(value):
            return value
        raise click.BadParameter(
            "Value '{}' does not look like valid email address.".format(value)
        )


user_cli = AppGroup('users')

@user_cli.command('create')
@click.argument('login', callback = validate_email)
@click.argument('fullname')
@click.option('--email', callback = validate_email, help = 'Optional email, login will be used as default')
@click.password_option()
@click.option('--enabled/--no-enabled', default=False)
def users_create(login, fullname, email, password, enabled):
    """
    Create user account.
    """
    sqlobj = mydojo.db.UserModel()

    sqlobj.login    = login
    sqlobj.fullname = fullname
    sqlobj.email    = email or login
    if password:
        sqlobj.set_password(password)
    sqlobj.enabled  = enabled

    click.echo("Creating new user account:")
    click.echo("    - Login:     {}".format(sqlobj.login))
    click.echo("    - Full name: {}".format(sqlobj.fullname))
    click.echo("    - Email:     {}".format(sqlobj.email))
    click.echo("    - Password:  {}".format(sqlobj.password))
    click.echo("    - Enabled:   {}".format(sqlobj.enabled))
    try:
        mydojo.db.SQLDB.session.add(sqlobj)
        mydojo.db.SQLDB.session.commit()
        click.secho(
            "[OK] User account was successfully created",
            fg = 'green'
        )

    except sqlalchemy.exc.IntegrityError as exc:
        mydojo.db.SQLDB.session.rollback()
        match = re.search('Key \((\w+)\)=\(([^)]+)\) already exists.', str(exc))
        if match:
            click.secho(
                "[FAIL] User account with {} '{}' already exists.".format(
                    match.group(1),
                    match.group(2)
                ),
                fg = 'red'
            )
        else:
            click.secho(
                "[FAIL] There already is an user account with similar data.",
                fg = 'red'
            )
            click.secho(
                "\n{}".format(exc),
                fg = 'blue'
            )

    except Exception:  # pylint: disable=locally-disabled,broad-except
        mydojo.db.SQLDB.session.rollback()
        click.echo(
            traceback.TracebackException(*sys.exc_info())
        )

@user_cli.command('delete')
@click.argument('login', callback = validate_email)
def users_delete(login):
    """
    Delete user account.
    """
    click.echo("Deleting user account '{}'".format(login))
    try:
        item = mydojo.db.SQLDB.session.query(
            mydojo.db.UserModel
        ).filter(
            mydojo.db.UserModel.login == login
        ).one()

        mydojo.db.SQLDB.session.delete(item)
        mydojo.db.SQLDB.session.commit()
        click.secho(
            "[OK] User account was successfully deleted",
            fg = 'green'
        )

    except Exception:  # pylint: disable=locally-disabled,broad-except
        mydojo.db.SQLDB.session.rollback()
        click.echo(
            traceback.TracebackException(*sys.exc_info())
        )

    except Exception:  # pylint: disable=locally-disabled,broad-except
        mydojo.db.SQLDB.session.rollback()
        click.echo(
            traceback.TracebackException(*sys.exc_info())
        )

@user_cli.command('list')
def users_list():
    """
    List all available user accounts.
    """
    try:
        items = mydojo.db.SQLDB.session.query(mydojo.db.UserModel).all()
        if items:
            click.echo("List of existing user accounts:")
            for item in items:
                click.echo("    - {}".format(item.login))
        else:
            click.echo("There are currently no user accounts in the database.")

    except Exception:  # pylint: disable=locally-disabled,broad-except
        mydojo.db.SQLDB.session.rollback()
        click.echo(
            traceback.TracebackException(*sys.exc_info())
        )

def setup_cli(app):
    """
    Setup custom application CLI commands.
    """
    app.cli.add_command(user_cli)
