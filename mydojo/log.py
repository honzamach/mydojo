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


def setup_logging_file(app):
    """
    Setup application logging via watched file (rotated by external command).
    """
    file_handler = WatchedFileHandler(
        app.config['MYDOJO_LOG_FILE']
    )
    file_handler.setLevel(
        logging.INFO
    )
    file_handler.setFormatter(
        logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        )
    )

    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('MyDojo: Logging startup')
