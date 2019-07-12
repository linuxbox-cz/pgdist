#!/bin/bash

#set script to exit on error
set -e

#set echo colors
BLACK="\033[0;30m"  
DARK_GRAY="\033[1;30m"
RED="\033[0;31m"
LIGHT_RED="\033[1;31m"
GREEN="\033[0;32m"
LIGHT_GREEN="\033[1;32m"
BROWN_ORANGE="\033[0;33m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
LIGHT_BLUE="\033[1;34m"
PURPLE="\033[0;35m"
LIGHT_PURPLE="\033[1;35m"
CYAN="\033[0;36m"
LIGHT_CYAN="\033[1;36m"
LIGHT_GRAY="\033[0;37m"
WHITE="\033[1;37m"
NC="\033[0m"

msg_inf() {
    echo -e "${GREEN}$1${NC}"
}
msg_dbg() {
    echo -e "${YELLOW}$1${NC}"
}
msg_dbg_1() {
    echo -e "${BROWN_ORANGE}$1${NC}"
}
msg_err() {
    echo -e "${RED}$1${NC}"
}

msg_inf "test pgdist | test init"
PWD_SELF=$(pwd)
rm -rf /tmp/pgdist_test

#start test
msg_dbg "test pgdist | init | project: pgdist_project_test, directory: /tmp/pgdist_test"

PGDIST_INIT="PGdist project inited in /tmp/pgdist_test/"
PGDIST_INIT_TEST=$(pgdist init pgdist_project_test /tmp/pgdist_test/)

if [ "$PGDIST_INIT_TEST" != "$PGDIST_INIT" ]
then
    msg_err "pgdist init | failed"
    msg_inf "correct: ${PGDIST_INIT}"
    msg_inf "you got: ${PGDIST_INIT_TEST}"
fi

msg_dbg "test pgdist | create schema | schema: pgdist_schema_test"

cd /tmp/pgdist_test/sql/
PGDIST_CREATE_SCHEMA="Schema pgdist_schema_test created."
PGDIST_CREATE_SCHEMA_TEST=$(pgdist create-schema pgdist_schema_test)

if [ "$PGDIST_CREATE_SCHEMA_TEST" != "$PGDIST_CREATE_SCHEMA" ]
then
    msg_err "pgdist create schema | failed"
    msg_inf "correct: ${PGDIST_CREATE_SCHEMA}"
    msg_inf "you got: ${PGDIST_CREATE_SCHEMA_TEST}"
fi

#copy files to schema
cd "${PWD_SELF}/"
cp test_1.sql /tmp/pgdist_test/sql/pgdist_schema_test/tables/
cp test_2.sql /tmp/pgdist_test/sql/pgdist_schema_test/tables/
cp test_3.sql /tmp/pgdist_test/sql/pgdist_schema_test/tables/
cd /tmp/pgdist_test/sql/

msg_dbg "test pgdist | status"
pgdist status

msg_dbg "test pgdist | add | file: test_1.sql"
pgdist add /tmp/pgdist_test/sql/pgdist_schema_test/tables/test_1.sql
msg_dbg_1 "test pgdist | status"
pgdist status

msg_dbg "test pgdist | rm | file: test_1.sql"
pgdist rm /tmp/pgdist_test/sql/pgdist_schema_test/tables/test_1.sql
msg_dbg_1 "test pgdist | status"
pgdist status

msg_dbg "test pgdist | add | files: test_1.sql, test_2.sql"
pgdist add /tmp/pgdist_test/sql/pgdist_schema_test/tables/test_1.sql /tmp/pgdist_test/sql/pgdist_schema_test/tables/test_2.sql
msg_dbg_1 "test pgdist | status"
pgdist status

msg_dbg "test pgdist | rm | files: test_1.sql, test_2.sql"
pgdist rm /tmp/pgdist_test/sql/pgdist_schema_test/tables/test_1.sql /tmp/pgdist_test/sql/pgdist_schema_test/tables/test_2.sql
msg_dbg_1 "test pgdist | status"
pgdist status

msg_dbg "test pgdist | add | files: test_1.sql, test_2.sql, test_3.sql"
pgdist add /tmp/pgdist_test/sql/pgdist_schema_test/tables/test_3.sql /tmp/pgdist_test/sql/pgdist_schema_test/tables/test_1.sql /tmp/pgdist_test/sql/pgdist_schema_test/tables/test_2.sql
msg_dbg_1 "test pgdist | status"
pgdist status

msg_dbg "test pgdist | test-load"
pgdist test-load

msg_dbg "test pgdist | diff-db"
python /mnt/dev1/work/tpopov/pgdist/src/pgdist.py diff-db postgres:596603142@localhost

msg_inf "${GREEN}test pgdist | finished"