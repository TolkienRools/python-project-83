#!/usr/bin/env bash

# Postgres allows connecting to a remote database using a database URL specified after the -d flag.
# The database URL can be obtained from the DATABASE_URL environment variable.
# This value should be set on the platform where the deployment is performed.
# After that, we can create tables using the database.sql file with the -f flag.

make install && psql -a -d $DATABASE_URL -f database.sql