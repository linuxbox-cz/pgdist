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
BROWN="\033[0;33m"
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

#set paths to project 1
PATH_TEST=$(pwd)
PATH_PGDIST=$(dirname $PATH_TEST)
PATH_PGDIST_SRC="${PATH_PGDIST}/src"
PATH_PGDIST_INSTALL="/usr/share/pgdist/install"
PATH_PROJECT="/tmp/pgdist_test_1"
PATH_SQL="${PATH_PROJECT}/sql"
PATH_SQL_DIST="${PATH_PROJECT}/sql_dist"
PATH_SQL_SCHEMA="${PATH_SQL}/pgdist_test_schema"
PATH_TABLES="${PATH_SQL_SCHEMA}/tables"
PATH_SCHEMAS="${PATH_SQL_SCHEMA}/schema"
PATH_FUNCTIONS="${PATH_SQL_SCHEMA}/functions"
PATH_DATA="${PATH_SQL_SCHEMA}/data"

#set coloured log
log() {
    echo -e "${GREEN}Test | ${WHITE}$1${NC}"
}
log_pgdist() {
    echo -e "${GREEN}Test | ${YELLOW}pgdist $1${NC}"
}
log_git() {
    echo -e "${GREEN}Test | ${BROWN}git $1${NC}"
}
log_wrn() {
    echo -e "${PURPLE}Test | warning: $1${NC}"
}
log_err() {
    echo -e "${RED}Test | error: $1${NC}"
}

clean_up() {
    log "cleaning up begin"
    cd $PATH_TEST
    rm -rfv --preserve-root --one-file-system -- $PATH_PROJECT
    rm -fv --preserve-root --one-file-system "${PATH_PGDIST_INSTALL}/pgdist_test_project--1.0--1.1.sql"
    rm -fv --preserve-root --one-file-system "${PATH_PGDIST_INSTALL}/pgdist_test_project--1.0.sql"
    rm -fv --preserve-root --one-file-system "${PATH_PGDIST_INSTALL}/pgdist_test_project_2--1.0.sql"
    psql -U postgres -c "DROP DATABASE IF EXISTS pgdist_test_database;"
    log "cleaning up finished"
}

#argument parsing
while [ "$1" != "" ]; do
    case $1 in
        -u | --user )
            shift
            GIT_USER_NAME=$1;;
        -e | --email )
            shift
            GIT_USER_EMAIL=$1;;
        -p | --pgconn )
            shift
            PGCONN=$1;;
        --no-clean )
            NO_CLEAN=true;;
        -h | --help )
            echo "Optional parameters:"
            echo "    -u --user     git user name"
            echo "    -e --email    git user email"
            echo "    -p --pgconn   pg connection"
            echo "    --no-clean    wont clean files and database after test"
            echo "    -h --help     prints this help"
            exit 0;;
        *)
    esac
    shift
done

if [ ! "$PGCONN" ]; then
    PGCONN="postgres:596603142@localhost"
fi
if [ ! "$NO_CLEAN" ]; then
    NO_CLEAN=false
fi
if [ ! "$GIT_USER_NAME" -o ! "$GIT_USER_EMAIL" ]; then
    GIT_USER_NAME="test user"
    GIT_USER_EMAIL="test@email.cz"
    GIT_RUN=false
    log_wrn "require-add test wont run!"
else
    GIT_RUN=true
fi

log "begin\n"
clean_up

log_pgdist "init pgdist_test_project ${PATH_PROJECT}"
python "${PATH_PGDIST_SRC}/pgdist.py" init pgdist_test_project "${PATH_PROJECT}/"

log_pgdist "create-schema pgdist_test_schema"
cd $PATH_SQL
python "${PATH_PGDIST_SRC}/pgdist.py" create-schema pgdist_test_schema

log "cp schema_1.sql ${PATH_SCHEMAS}/"
cd $PATH_TEST
cp schema_1.sql "${PATH_SCHEMAS}/"

log "cp table_1.sql ${PATH_TABLES}/"
cp table_1.sql "${PATH_TABLES}/"

log "cp table_2.sql ${PATH_TABLES}/"
cp table_2.sql "${PATH_TABLES}/"

log "cp pgdist_test_project_2--1.0.sql ${PATH_PGDIST_INSTALL}"
cp pgdist_test_project_2--1.0.sql "${PATH_PGDIST_INSTALL}/"

#FILES
log_pgdist "status"
cd $PATH_SQL
python "${PATH_PGDIST_SRC}/pgdist.py" status

log_pgdist "add ${PATH_TABLES}/table_1.sql"
python "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_TABLES}/table_1.sql"

log_pgdist "status"
python "${PATH_PGDIST_SRC}/pgdist.py" status

log_pgdist "rm ${PATH_TABLES}/table_1.sql"
python "${PATH_PGDIST_SRC}/pgdist.py" rm "${PATH_TABLES}/table_1.sql"

log_pgdist "status"
python "${PATH_PGDIST_SRC}/pgdist.py" status

log_pgdist "add ${PATH_TABLES}/table_1.sql ${PATH_TABLES}/table_2.sql"
python "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_TABLES}/table_1.sql" "${PATH_TABLES}/table_2.sql"

log_pgdist "status"
python "${PATH_PGDIST_SRC}/pgdist.py" status

log_pgdist "rm ${PATH_TABLES}/table_1.sql ${PATH_TABLES}/table_2.sql"
python "${PATH_PGDIST_SRC}/pgdist.py" rm "${PATH_TABLES}/table_1.sql" "${PATH_TABLES}/table_2.sql"

log_pgdist "status"
python "${PATH_PGDIST_SRC}/pgdist.py" status

log_pgdist "add ${PATH_SCHEMAS}/schema_1.sql ${PATH_TABLES}/table_1.sql ${PATH_TABLES}/table_2.sql"
python "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_SCHEMAS}/schema_1.sql" "${PATH_TABLES}/table_1.sql" "${PATH_TABLES}/table_2.sql"

log_pgdist "status"
python "${PATH_PGDIST_SRC}/pgdist.py" status

#DIFF
log_pgdist "diff-db ${PGCONN} --no-owner --no-acl"
python "${PATH_PGDIST_SRC}/pgdist.py" diff-db ${PGCONN} --no-owner --no-acl -U postgres

log_pgdist "diff-db-file ${PGCONN} '${PATH_SCHEMAS}/schema_1.sql' --no-owner --no-acl"
python "${PATH_PGDIST_SRC}/pgdist.py" diff-db-file ${PGCONN} "${PATH_SCHEMAS}/schema_1.sql" --no-owner --no-acl -U postgres

log_pgdist "diff-file-db '${PATH_SCHEMAS}/schema_1.sql' ${PGCONN} --no-owner --no-acl"
python "${PATH_PGDIST_SRC}/pgdist.py" diff-file-db "${PATH_SQL}/pg_project.sql" ${PGCONN} --no-owner --no-acl -U postgres

log_pgdist "test-load"
cd $PATH_PROJECT
python "${PATH_PGDIST_SRC}/pgdist.py" test-load -U postgres

log_pgdist "create-version 1.0"
cd $PATH_SQL
python "${PATH_PGDIST_SRC}/pgdist.py" create-version 1.0

#GIT
log_git "init"
cd $PATH_PROJECT
git init

log_git "config user.name '${GIT_USER_NAME}'"
cd $PATH_PROJECT
git config user.name $GIT_USER_NAME

log_git "config user.email '${GIT_USER_EMAIL}'"
git config user.email $GIT_USER_EMAIL

log_git "add ."
git add .

log_git "commit -m 'test pgdist 1.0'"
git commit -m "test pgdist 1.0"

log_git "tag -a v1.0 -m 'test pgdist v1.0'"
git tag -a v1.0 -m "test pgdist v1.0"

log "mkdir ${PATH_DATA}"
mkdir $PATH_DATA

log "cp function_1.sql ${PATH_FUNCTIONS}/"
cd $PATH_TEST
cp function_1.sql "${PATH_FUNCTIONS}/"

log "cp data_1.sql ${PATH_DATA}/"
cp data_1.sql "${PATH_DATA}/"

log_pgdist "add ${PATH_FUNCTIONS}/function_1.sql"
cd $PATH_SQL
python "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_FUNCTIONS}/function_1.sql"

log_pgdist "add ${PATH_DATA}/data_1.sql"
python "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_DATA}/data_1.sql"

#ROLES
log_pgdist "role-list"
python "${PATH_PGDIST_SRC}/pgdist.py" role-list

log_pgdist "role-add pgdist_test_role_1 nologin"
python "${PATH_PGDIST_SRC}/pgdist.py" role-add pgdist_test_role_1 nologin

log_pgdist "role-list"
python "${PATH_PGDIST_SRC}/pgdist.py" role-list

log_pgdist "role-add pgdist_test_role_2 login password123"
python "${PATH_PGDIST_SRC}/pgdist.py" role-add pgdist_test_role_2 login password123

log_pgdist "role-list"
python "${PATH_PGDIST_SRC}/pgdist.py" role-list

log_pgdist "role-rm pgdist_test_role_1"
python "${PATH_PGDIST_SRC}/pgdist.py" role-rm pgdist_test_role_1

log_pgdist "role-rm pgdist_test_role_2"
python "${PATH_PGDIST_SRC}/pgdist.py" role-rm pgdist_test_role_2

log_pgdist "role-list"
python "${PATH_PGDIST_SRC}/pgdist.py" role-list

log_pgdist "role-add pgdist_test_role_1 nologin"
python "${PATH_PGDIST_SRC}/pgdist.py" role-add pgdist_test_role_1 nologin

log_pgdist "role-add pgdist_test_role_2 login password123"
python "${PATH_PGDIST_SRC}/pgdist.py" role-add pgdist_test_role_2 login password123

log_pgdist "role-change pgdist_test_role_1 login password123"
python "${PATH_PGDIST_SRC}/pgdist.py" role-change pgdist_test_role_1 login password123

log_pgdist "role-change pgdist_test_role_2 nologin "
python "${PATH_PGDIST_SRC}/pgdist.py" role-change pgdist_test_role_1 nologin

log_pgdist "role-list"
python "${PATH_PGDIST_SRC}/pgdist.py" role-list

#DBPARAM
log_pgdist "dbparam-set OWNER pgdist_test_role_1"
python "${PATH_PGDIST_SRC}/pgdist.py" dbparam-set OWNER pgdist_test_role_1

log_pgdist "dbparam-get"
python "${PATH_PGDIST_SRC}/pgdist.py" dbparam-get

if [ "$GIT_RUN" = true ]; then
    log_pgdist "require-add pgdist_test_project_2 git@git.linuxbox.cz:tpopov/pgdist_tester.git master"
    pgdist require-add pgdist_test_project_2 git@git.linuxbox.cz:tpopov/pgdist_tester.git master
fi

#DATA
log_pgdist "data-add pgdist_test_schema.test_table_1"
python "${PATH_PGDIST_SRC}/pgdist.py" data-add pgdist_test_schema.test_table_1

log_pgdist "data-list"
python "${PATH_PGDIST_SRC}/pgdist.py" data-list

log_pgdist "data-rm pgdist_test_schema.test_table_1"
python "${PATH_PGDIST_SRC}/pgdist.py" data-rm pgdist_test_schema.test_table_1

log_pgdist "data-list"
python "${PATH_PGDIST_SRC}/pgdist.py" data-list

log_pgdist "data-add pgdist_test_schema.test_table_1"
python "${PATH_PGDIST_SRC}/pgdist.py" data-add pgdist_test_schema.test_table_1

#UPDATE
log_pgdist "create-update v1.0 1.1"
python "${PATH_PGDIST_SRC}/pgdist.py" create-update v1.0 1.1

log "cp -a ${PATH_SQL_DIST}/. ${PATH_PGDIST_INSTALL}"
cp -a "${PATH_SQL_DIST}/." $PATH_PGDIST_INSTALL

log_pgdist "test-update v1.0 1.1"
cd $PATH_SQL
python "${PATH_PGDIST_SRC}/pgdist.py" test-update v1.0 1.1 -U postgres

#GIT
log_git "add ."
cd $PATH_PROJECT
git add .

log_git "commit -m 'test pgdist 1.1'"
git commit -m "test pgdist 1.1"

log_git "tag -a v1.1 -m 'test pgdist v1.1'"
git tag -a v1.1 -m "test pgdist v1.1"

log_git "tag -l"
git tag -l

log_pgdist "list -U postgres"
python "${PATH_PGDIST_SRC}/pgdist.py" list -U postgres

log "psql -U postgres -c 'CREATE DATABASE pgdist_test_database;'"
psql -U postgres -c "CREATE DATABASE pgdist_test_database;"

#INSTALL PROJECT
log_pgdist "install pgdist_test_project pgdist_test_database"
python "${PATH_PGDIST_SRC}/pgdist.py" install pgdist_test_project pgdist_test_database -U postgres

log "psql -U postgres -d pgdist_test_database -c 'SELECT * FROM pgdist_test_schema.test_table_1;'"
psql -U postgres -d pgdist_test_database -c "SELECT * FROM pgdist_test_schema.test_table_1;"

log_pgdist "list -U postgres"
python "${PATH_PGDIST_SRC}/pgdist.py" list -U postgres

log_pgdist "diff-db ${PGCONN} v1.0"
python "${PATH_PGDIST_SRC}/pgdist.py" diff-db ${PGCONN} v1.0 -U postgres

#UPDATE
log_pgdist "check-update pgdist_test_project pgdist_test_database"
python "${PATH_PGDIST_SRC}/pgdist.py" check-update pgdist_test_project pgdist_test_database -U postgres

log_pgdist "update pgdist_test_project pgdist_test_database 1.1"
python "${PATH_PGDIST_SRC}/pgdist.py" update pgdist_test_project pgdist_test_database 1.1 -U postgres

if [ "$GIT_RUN" = true ]; then
    log "psql -U postgres -d pgdist_test_database -c 'SELECT * FROM pgdist_test_schema_2.test_table_1;'"
    psql -U postgres -d pgdist_test_database -c "SELECT * FROM pgdist_test_schema_2.test_table_1;"
fi

log_pgdist "list -U postgres"
python "${PATH_PGDIST_SRC}/pgdist.py" list -U postgres

log_pgdist "pgdist-update pgdist_test_database"
python "${PATH_PGDIST_SRC}/pgdist.py" pgdist-update pgdist_test_database -U postgres

log_pgdist "set-version pgdist_test_project pgdist_test_database 2.0"
python "${PATH_PGDIST_SRC}/pgdist.py" set-version pgdist_test_project pgdist_test_database 2.0 -U postgres

log_pgdist "list -U postgres"
python "${PATH_PGDIST_SRC}/pgdist.py" list -U postgres

log_pgdist "clean pgdist_test_project pgdist_test_database"
python "${PATH_PGDIST_SRC}/pgdist.py" clean pgdist_test_project pgdist_test_database -U postgres

if [ "$GIT_RUN" = true ]; then
    log_pgdist "require-rm pgdist_test_project_2"
    pgdist require-rm pgdist_test_project_2
fi

log "finished"

if [ "$NO_CLEAN" = false ]; then
    clean_up
fi
