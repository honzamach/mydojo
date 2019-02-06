#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


"""
MyDojo - local development server

This command will launch built-in development HTTP server and bind it to ``localhost``,
port ``5000``. It will also force the debug mode to ``True``.

Usage
--------------------------------------------------------------------------------

Just execute with Python3 interpreter::

    python3 mydojo-dev.py

Now point your browser to ``localhost``, port ``5000``::

    http://localhost:5000

License
--------------------------------------------------------------------------------

Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
Use of this source is governed by the MIT license.
"""


__author__ = "Honza Mach <honza.mach.ml@gmail.com>"


if __name__ == '__main__':

    import mydojo

    #
    # Use prepared factory function to create application instance. The factory
    # function takes number of arguments, that can be used to fine tune coniguration
    # of the application. This is can be very usefull when extending applications`
    # capabilities or for purposes of testing. Please refer to the documentation
    # for more information.
    #
    APP = mydojo.create_app(
        config_object = 'mydojo.config.DevelopmentConfig'
    )

    #
    # Launch WSGI application, bind to localhost:5000 and enforce debug mode to True.
    #
    APP.run(
        host  = '127.0.0.1',
        port  = 5000,
        debug = True
    )
