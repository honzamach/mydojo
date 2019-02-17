#-------------------------------------------------------------------------------
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


import mydojo


#
# Use prepared factory function to create application instance. The factory
# function takes number of arguments, that can be used to fine tune coniguration
# of the application. This is can be very usefull when extending applications`
# capabilities or for purposes of testing. Please refer to the documentation
# for more information.
#
application = mydojo.create_app_full(
    config_object = 'mydojo.config.ProductionConfig',
    config_file   = '/etc/mydojo/mydojo.conf',
    config_env    = 'FLASK_CONFIG_FILE'
)
