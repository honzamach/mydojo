#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
This module contains logging functions for MyDojo.
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


import logging
from logging.handlers import WatchedFileHandler, SMTPHandler


def setup_logging_default(app):
    """
    Setup default application logging features.
    """
    log_level_str = app.config['MYDOJO_LOG_DEFAULT_LEVEL'].upper()
    log_level = getattr(
        logging,
        log_level_str,
        None
    )
    if not isinstance(log_level, int):
        raise ValueError(
            'Invalid default log level: %s' % log_level_str
        )

    app.logger.setLevel(log_level)
    app.logger.debug(
        'MyDojo: Default logging services successfully started with level %s',
        log_level_str
    )

    return app

def setup_logging_file(app):
    """
    Setup application logging via watched file (rotated by external command).
    """
    log_level_str = app.config['MYDOJO_LOG_FILE_LEVEL'].upper()
    log_level = getattr(
        logging,
        log_level_str,
        None
    )
    if not isinstance(log_level, int):
        raise ValueError(
            'Invalid log file level: %s' % log_level_str
        )

    file_handler = WatchedFileHandler(app.config['MYDOJO_LOG_FILE'])
    file_handler.setLevel(log_level)
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
    )

    app.logger.addHandler(file_handler)
    app.logger.debug(
        'MyDojo: File logging services successfully started to file %s with level %s',
        app.config['MYDOJO_LOG_FILE'],
        log_level_str
    )

    return app

def setup_logging_email(app):
    """
    Setup application logging via email.
    """
    log_level_str = app.config['MYDOJO_LOG_EMAIL_LEVEL'].upper()
    log_level = getattr(
        logging,
        log_level_str,
        None
    )
    if not isinstance(log_level, int):
        raise ValueError(
            'Invalid log email level: %s' % log_level_str
        )

    credentials = None
    secure = None
    if app.config['MAIL_USERNAME']:
        credentials = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        if app.config['MAIL_USE_TLS']:
            secure = ()

    mail_handler = SMTPHandler(
        mailhost = (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
        fromaddr = app.config['MAIL_DEFAULT_SENDER'],
        toaddrs = app.config['MYDOJO_ADMINS'],
        subject = app.config['MAIL_SUBJECT_PREFIX'] + ' Application Error',
        credentials = credentials,
        secure = secure
    )
    mail_handler.setLevel(log_level)
    mail_handler.setFormatter(
        logging.Formatter('''
Message type: %(levelname)s
Location:     %(pathname)s:%(lineno)d
Module:       %(module)s
Function:     %(funcName)s
Time:         %(asctime)s

Message:

%(message)s
'''))

    app.logger.addHandler(mail_handler)
    app.logger.debug(
        'MyDojo: Email logging services successfully started with level %s',
        log_level_str
    )

    return app
