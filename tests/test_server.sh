#!/bin/bash

TEST_PART="server | "
log "test begin\n"

log_pgdist "list"
python "${PATH_PGDIST_SRC}/pgdist.py" list -c $PATH_CONFIG_MNG

log "psql -U postgres -c 'CREATE DATABASE pgdist_test_database;'"
psql -U postgres -c "CREATE DATABASE pgdist_test_database;"

#install project to db
log_pgdist "install pgdist_test_project pgdist_test_database"
python "${PATH_PGDIST_SRC}/pgdist.py" install pgdist_test_project pgdist_test_database -c $PATH_CONFIG_MNG

log "psql -U postgres -d pgdist_test_database -c 'SELECT * FROM pgdist_test_schema.test_table_1;'"
psql -U postgres -d pgdist_test_database -c "SELECT * FROM pgdist_test_schema.test_table_1;"

log_pgdist "list"
python "${PATH_PGDIST_SRC}/pgdist.py" list -c $PATH_CONFIG_MNG

PGCONN="postgres@/pgdist_test_database"
log_pgdist "diff-db ${PGCONN}"
python "${PATH_PGDIST_SRC}/pgdist.py" diff-db $PGCONN -c $PATH_CONFIG_DEV

#update db project
log_pgdist "check-update pgdist_test_project pgdist_test_database"
python "${PATH_PGDIST_SRC}/pgdist.py" check-update pgdist_test_project pgdist_test_database -c $PATH_CONFIG_MNG

log_pgdist "update pgdist_test_project pgdist_test_database 1.1"
python "${PATH_PGDIST_SRC}/pgdist.py" update pgdist_test_project pgdist_test_database 1.1 -c $PATH_CONFIG_MNG

log "psql -U postgres -d pgdist_test_database -c 'SELECT * FROM pgdist_test_schema_3.test_table_1;'"
psql -U postgres -d pgdist_test_database -c "SELECT * FROM pgdist_test_schema_3.test_table_1;"

if [ "$GIT_RUN" = true ]; then
    log "psql -U postgres -d pgdist_test_database -c 'SELECT * FROM pgdist_test_schema_2.test_table_1;'"
    psql -U postgres -d pgdist_test_database -c "SELECT * FROM pgdist_test_schema_2.test_table_1;"
fi

#test diff-db/db-file/file-db
log_pgdist "diff-db ${PGCONN}"
python "${PATH_PGDIST_SRC}/pgdist.py" diff-db $PGCONN -c $PATH_CONFIG_DEV

log_pgdist "diff-db-file ${PGCONN} '${PATH_SQL}/pg_project.sql'"
python "${PATH_PGDIST_SRC}/pgdist.py" diff-db-file "${PGCONN}" "${PATH_SQL}/pg_project.sql" -c $PATH_CONFIG_DEV

log_pgdist "diff-file-db '${PATH_SQL}/pg_project.sql' ${PGCONN}"
python "${PATH_PGDIST_SRC}/pgdist.py" diff-file-db "${PATH_SQL}/pg_project.sql" $PGCONN -c $PATH_CONFIG_DEV

log_pgdist "list"
python "${PATH_PGDIST_SRC}/pgdist.py" list -c $PATH_CONFIG_MNG

log_pgdist "pgdist-update pgdist_test_database"
python "${PATH_PGDIST_SRC}/pgdist.py" pgdist-update pgdist_test_database -c $PATH_CONFIG_MNG

log_pgdist "set-version pgdist_test_project pgdist_test_database 2.0"
python "${PATH_PGDIST_SRC}/pgdist.py" set-version pgdist_test_project pgdist_test_database 2.0 -c $PATH_CONFIG_MNG

log_pgdist "list"
python "${PATH_PGDIST_SRC}/pgdist.py" list -c $PATH_CONFIG_MNG

log "test 3/3 finished"
