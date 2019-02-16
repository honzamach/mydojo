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
from logging.handlers import WatchedFileHandler


def setup_logging_default(app):
    """
    Setup default application logging features.
    """
    log_level = getattr(
        logging,
        app.config['MYDOJO_LOG_DEFAULT_LEVEL'].upper(),
        None
    )
    if not isinstance(log_level, int):
        raise ValueError('Invalid default log level: %s' % app.config['MYDOJO_LOG_DEFAULT_LEVEL'])

    app.logger.setLevel(log_level)
    app.logger.debug('MyDojo: Default logging services successfully started')

    return app

def setup_logging_file(app):
    """
    Setup application logging via watched file (rotated by external command).
    """
    log_file_level = getattr(
        logging,
        app.config['MYDOJO_LOG_FILE_LEVEL'].upper(),
        None
    )
    if not isinstance(log_file_level, int):
        raise ValueError('Invalid log file level: %s' % app.config['MYDOJO_LOG_FILE_LEVEL'])

    file_handler = WatchedFileHandler(app.config['MYDOJO_LOG_FILE'])
    file_handler.setLevel(log_file_level)
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
    )

    app.logger.addHandler(file_handler)
    app.logger.debug('MyDojo: File logging services successfully started')

    return app
