#!/bin/bash
#-------------------------------------------------------------------------------
# CONVENIENCE SCRIPT FOR CREATING POSTGRESQL USER AND DATABASES FOR MYDOJO
#
# Usage
# -----
#
# 1. Create default 'mydojo' user with 'mydojo' password and 'mydojo' and
#    'mydojo_test' databases:
#
#	mydojo-init.sh
#
# 2. Use positional parameters to override user name, password and database name:
#
#	mydojo-init.sh myuser mypass mydbname
#
#
# This file is part of MyDojo package (https://github.com/honzamach/mydojo).
#
# Copyright (C) since 2018 Honza Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------


#
# These parameters may be overridden from command line.
#
USER=${1:-mydojo}
PASS=${2:-mydojo}
DBNM=${3:-mydojo}

cd /

#
# Create database user.
#
sudo -u postgres psql -c "SELECT usename FROM pg_catalog.pg_user;" | grep $USER > /dev/null
if [ $? -ne 0 ]; then
    echo "PostgreSQL: Creating user '$USER'"
    sudo -u postgres psql -c "CREATE USER $USER WITH PASSWORD '$PASS';"
fi

#
# Create databases.
#
for dbname in "${DBNM}" "${DBNM}_test"
do
    sudo -u postgres psql -c "SELECT datname FROM pg_catalog.pg_database;" | grep $dbname > /dev/null
    if [ $? -ne 0 ]; then
        echo "PostgreSQL: Creating database '$dbname'"
        sudo -u postgres psql -c "CREATE DATABASE $dbname;"
        echo "PostgreSQL: Granting access for user '$USER' to database '$dbname'"
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $dbname TO $USER;"
    fi
done
