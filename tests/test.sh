#!/bin/bash

#script exits on error
set -e

#echo colors
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

#paths to project 1
PATH_TEST=$(pwd)
PATH_D1="${PATH_TEST}/sql_devel_1"
PATH_D2="${PATH_TEST}/sql_devel_2"
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
PATH_CONSTRAINTS="${PATH_SQL_SCHEMA}/constraints"
PATH_TRIGGERS="${PATH_SQL_SCHEMA}/triggers"
PATH_INDEXES="${PATH_SQL_SCHEMA}/indexes"
PATH_DATA="${PATH_SQL_SCHEMA}/data"
PATH_VIEWS="${PATH_SQL_SCHEMA}/views"
CONFIG_FILE=".pgdist"
PATH_CONFIG="~/${CONFIG_FILE}"

TEST_PART=""

#coloured log
log() {
    echo -e "${GREEN}Test | ${TEST_PART}${WHITE}$1${NC}"
}
log_pgdist() {
    echo -e "${GREEN}Test | ${TEST_PART}${YELLOW}pgdist $1${NC}"
}
log_git() {
    echo -e "${GREEN}Test | ${TEST_PART}${BROWN}git $1${NC}"
}
log_wrn() {
    echo -e "${PURPLE}Test | ${TEST_PART}warning: $1${NC}"
}
log_err() {
    echo -e "${RED}Test | ${TEST_PART}error: $1${NC}"
}

#clean up functions
clean_up() {
    log "cleaning up begin"
    cd $PATH_TEST
    rm -rfv --preserve-root --one-file-system -- $PATH_PROJECT
    rm -fv --preserve-root --one-file-system "${PATH_PGDIST_INSTALL}/pgdist_test_project--1.0--1.1.sql"
    rm -fv --preserve-root --one-file-system "${PATH_PGDIST_INSTALL}/pgdist_test_project--1.0.sql"
    rm -fv --preserve-root --one-file-system "${PATH_PGDIST_INSTALL}/pgdist_test_project_2--1.0.sql"
    if [ "$CLEAN_CONFIG" = true ]; then
        rm -fv --preserve-root --one-file-system $PATH_CONFIG
    fi
    psql -U postgres -c "DROP DATABASE IF EXISTS pgdist_test_database;"
    psql -U postgres -c "DROP ROLE IF EXISTS pgdist_test_role_1;"
    psql -U postgres -c "DROP ROLE IF EXISTS pgdist_test_role_2;"
    log "cleaning up finished"
}

#argument parsing
while [ "$1" != "" ]; do
    case $1 in
        -u | --user )
            shift
            GIT_USER=$1;;
        -e | --email )
            shift
            GIT_EMAIL=$1;;
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
    PGCONN="postgres:password@localhost"
fi
if [ ! "$NO_CLEAN" ]; then
    NO_CLEAN=false
fi

#clean and init config if does not exist
CLEAN_CONFIG=false
clean_up
cd ~

if [ ! -e "$CONFIG_FILE" ]; then
    log "echo '[pgdist]' >> ${CONFIG_FILE}"
    echo "[pgdist]" >> $CONFIG_FILE

    log "echo 'test_db: postgres:password@localhost' >> ${CONFIG_FILE}"
    echo "test_db: postgres:password@localhost" >> $CONFIG_FILE

    log "echo 'install_path: /usr/share/pgdist/install' >> ${CONFIG_FILE}"
    echo "install_path: /usr/share/pgdist/install" >> $CONFIG_FILE
    CLEAN_CONFIG=true
fi

#test pgdist devel_1
source "${PATH_TEST}/test_devel_1.sh"

#test pgdist devel_2
source "${PATH_TEST}/test_devel_2.sh"

#test pgdist server.sh
source "${PATH_TEST}/test_server.sh"

if [ "$NO_CLEAN" = false ]; then
    log_pgdist "clean pgdist_test_project pgdist_test_database"
    python "${PATH_PGDIST_SRC}/pgdist.py" clean pgdist_test_project pgdist_test_database
fi

TEST_PART=""
log "succes!"

if [ "$NO_CLEAN" = false ]; then
    clean_up
fi
