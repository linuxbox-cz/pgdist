#!/bin/bash

TEST_PART="devel_1 | "
log "test begin\n"

#init pgdist project
log_pgdist "init pgdist_test_project ${PATH_PROJECT}"
python "${PATH_PGDIST_SRC}/pgdist.py" init pgdist_test_project "${PATH_PROJECT}/" -c "${PATH_CONFIG}"

#create pgdist schema
log_pgdist "create-schema pgdist_test_schema"
cd $PATH_SQL
python "${PATH_PGDIST_SRC}/pgdist.py" create-schema pgdist_test_schema -c "${PATH_CONFIG}"

#git setup
log_git "init"
cd $PATH_PROJECT
git init

if [ "$GIT_USER" -a "$GIT_EMAIL" ]; then
    log_git "config user.name ${GIT_USER}"
    git config --local user.name $GIT_USER

    log_git "config user.email ${GIT_EMAIL}"
    git config --local user.email $GIT_EMAIL

    GIT_RUN=true
fi

#copy sql files to project directory
log "cp ${PATH_D1}/d1_schema_1.sql ${PATH_SCHEMAS}/"
cd $PATH_TEST
cp "${PATH_D1}/d1_schema_1.sql" "${PATH_SCHEMAS}/"

log "cp ${PATH_D1}/d1_table_1.sql ${PATH_TABLES}/"
cp "${PATH_D1}/d1_table_1.sql" "${PATH_TABLES}/"

log "cp ${PATH_D1}/d1_table_2.sql ${PATH_TABLES}/"
cp "${PATH_D1}/d1_table_2.sql" "${PATH_TABLES}/"

log "cp ${PATH_D1}/d1_function_1.sql ${PATH_FUNCTIONS}/"
cp "${PATH_D1}/d1_function_1.sql" "${PATH_FUNCTIONS}/"

log "cp ${PATH_D1}/d1_index_1.sql ${PATH_INDEXES}/"
cp "${PATH_D1}/d1_index_1.sql" "${PATH_INDEXES}/"

log "cp ${PATH_D1}/d1_constraint_1.sql ${PATH_CONSTRAINTS}/"
cp "${PATH_D1}/d1_constraint_1.sql" "${PATH_CONSTRAINTS}/"

log "cp ${PATH_D1}/d1_view_1.sql ${PATH_VIEWS}/"
cp "${PATH_D1}/d1_view_1.sql" "${PATH_VIEWS}/"

log "cp ${PATH_D1}/d1_data_1.sql ${PATH_DATA}/"
cp "${PATH_D1}/d1_data_1.sql" "${PATH_DATA}/"

log "cp ${PATH_D1}/d1_trigger_1.sql ${PATH_TRIGGERS}/"
cp "${PATH_D1}/d1_trigger_1.sql" "${PATH_TRIGGERS}/"

log "mkdir -p ${PATH_PGDIST_INSTALL}"
mkdir -p $PATH_PGDIST_INSTALL

log "cp pgdist_test_project_2--1.0.sql ${PATH_PGDIST_INSTALL}"
cp pgdist_test_project_2--1.0.sql "${PATH_PGDIST_INSTALL}/"

#add and remove files from project
log_pgdist "status"
cd $PATH_SQL
python "${PATH_PGDIST_SRC}/pgdist.py" status -c "${PATH_CONFIG_1}"

log_pgdist "add ${PATH_TABLES}/d1_table_1.sql"
python "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_TABLES}/d1_table_1.sql"

log_pgdist "status"
python "${PATH_PGDIST_SRC}/pgdist.py" status -c "${PATH_CONFIG_1}"

log_pgdist "rm ${PATH_TABLES}/d1_table_1.sql"
python "${PATH_PGDIST_SRC}/pgdist.py" rm "${PATH_TABLES}/d1_table_1.sql"

log_pgdist "status"
python "${PATH_PGDIST_SRC}/pgdist.py" status -c "${PATH_CONFIG_1}"

log_pgdist "add ${PATH_TABLES}/d1_table_1.sql ${PATH_TABLES}/d1_table_2.sql"
python "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_TABLES}/d1_table_1.sql" "${PATH_TABLES}/d1_table_2.sql" -c "${PATH_CONFIG_1}"

log_pgdist "status"
python "${PATH_PGDIST_SRC}/pgdist.py" status -c "${PATH_CONFIG_1}"

log_pgdist "rm ${PATH_TABLES}/d1_table_1.sql ${PATH_TABLES}/d1_table_2.sql"
python "${PATH_PGDIST_SRC}/pgdist.py" rm "${PATH_TABLES}/d1_table_1.sql" "${PATH_TABLES}/d1_table_2.sql" -c "${PATH_CONFIG_1}"

log_pgdist "status"
python "${PATH_PGDIST_SRC}/pgdist.py" status -c "${PATH_CONFIG_1}"

log_pgdist "add ${PATH_SCHEMAS}/d1_schema_1.sql ${PATH_TABLES}/d1_table_1.sql ${PATH_TABLES}/d1_table_2.sql ${PATH_FUNCTIONS}/d1_function_1.sql"
python "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_SCHEMAS}/d1_schema_1.sql" "${PATH_TABLES}/d1_table_1.sql" "${PATH_TABLES}/d1_table_2.sql" "${PATH_FUNCTIONS}/d1_function_1.sql" -c "${PATH_CONFIG_1}"

log_pgdist "add ${PATH_INDEXES}/d1_index_1.sql ${PATH_CONSTRAINTS}/d1_constraint_1.sql ${PATH_TRIGGERS}/d1_trigger_1.sql ${PATH_VIEWS}/d1_view_1.sql ${PATH_DATA}/d1_data_1.sql"
python "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_INDEXES}/d1_index_1.sql" "${PATH_CONSTRAINTS}/d1_constraint_1.sql" "${PATH_TRIGGERS}/d1_trigger_1.sql" "${PATH_VIEWS}/d1_view_1.sql" "${PATH_DATA}/d1_data_1.sql" -c "${PATH_CONFIG_1}"

log_pgdist "status"
python "${PATH_PGDIST_SRC}/pgdist.py" status -c "${PATH_CONFIG_1}"

#add and remove roles
log_pgdist "role-list"
python "${PATH_PGDIST_SRC}/pgdist.py" role-list -c "${PATH_CONFIG_1}"

log_pgdist "role-add pgdist_test_role_1 nologin"
python "${PATH_PGDIST_SRC}/pgdist.py" role-add pgdist_test_role_1 nologin -c "${PATH_CONFIG_1}"

log_pgdist "role-list"
python "${PATH_PGDIST_SRC}/pgdist.py" role-list -c "${PATH_CONFIG_1}"

log_pgdist "role-rm pgdist_test_role_1"
python "${PATH_PGDIST_SRC}/pgdist.py" role-rm pgdist_test_role_1 -c "${PATH_CONFIG_1}"

log_pgdist "role-list"
python "${PATH_PGDIST_SRC}/pgdist.py" role-list -c "${PATH_CONFIG_1}"

log_pgdist "role-add pgdist_test_role_1 login password"
python "${PATH_PGDIST_SRC}/pgdist.py" role-add pgdist_test_role_1 login password -c "${PATH_CONFIG_1}"

log_pgdist "role-list"
python "${PATH_PGDIST_SRC}/pgdist.py" role-list -c "${PATH_CONFIG_1}"

log_pgdist "role-rm pgdist_test_role_1"
python "${PATH_PGDIST_SRC}/pgdist.py" role-rm pgdist_test_role_1 -c "${PATH_CONFIG_1}"

log_pgdist "role-add pgdist_test_role_1 nologin"
python "${PATH_PGDIST_SRC}/pgdist.py" role-add pgdist_test_role_1 nologin -c "${PATH_CONFIG_1}"

log_pgdist "role-add pgdist_test_role_2 login password"
python "${PATH_PGDIST_SRC}/pgdist.py" role-add pgdist_test_role_2 login password -c "${PATH_CONFIG_1}"

#set and get dbparam
log_pgdist "dbparam-set OWNER pgdist_test_role_1"
python "${PATH_PGDIST_SRC}/pgdist.py" dbparam-set OWNER pgdist_test_role_1 -c "${PATH_CONFIG_1}"

log_pgdist "dbparam-get"
python "${PATH_PGDIST_SRC}/pgdist.py" dbparam-get -c "${PATH_CONFIG_1}"

#add and remove require
log_pgdist "require-add pgdist_test_project_2 https://github.com/TadeasPopov/pgdist_test_project.git master"
python "${PATH_PGDIST_SRC}/pgdist.py" require-add pgdist_test_project_2 https://github.com/TadeasPopov/pgdist_test_project.git master -c "${PATH_CONFIG_1}"

log_pgdist "require-rm pgdist_test_project_2"
python "${PATH_PGDIST_SRC}/pgdist.py" require-rm pgdist_test_project_2 -c "${PATH_CONFIG_1}"

if [ "$GIT_USER" -a "$GIT_EMAIL" ]; then
    log_pgdist "require-add pgdist_test_project_2 https://github.com/TadeasPopov/pgdist_test_project.git master"
    python "${PATH_PGDIST_SRC}/pgdist.py" require-add pgdist_test_project_2 https://github.com/TadeasPopov/pgdist_test_project.git master -c "${PATH_CONFIG_1}"
fi

#add some data
log_pgdist "data-add pgdist_test_schema.test_table_1"
python "${PATH_PGDIST_SRC}/pgdist.py" data-add pgdist_test_schema.test_table_1 id -c "${PATH_CONFIG_1}"

log_pgdist "data-list"
python "${PATH_PGDIST_SRC}/pgdist.py" data-list -c "${PATH_CONFIG_1}"

log_pgdist "data-rm pgdist_test_schema.test_table_1"
python "${PATH_PGDIST_SRC}/pgdist.py" data-rm pgdist_test_schema.test_table_1 -c "${PATH_CONFIG_1}"

log_pgdist "data-list"
python "${PATH_PGDIST_SRC}/pgdist.py" data-list -c "${PATH_CONFIG_1}"

log_pgdist "data-add pgdist_test_schema.test_table_1 id"
python "${PATH_PGDIST_SRC}/pgdist.py" data-add pgdist_test_schema.test_table_1 id -c "${PATH_CONFIG_1}"

#try load project to test db
log_pgdist "test-load"
cd $PATH_PROJECT
python "${PATH_PGDIST_SRC}/pgdist.py" test-load -c "${PATH_CONFIG_1}"

#create version 1.0
log_pgdist "create-version 1.0"
cd $PATH_SQL
python "${PATH_PGDIST_SRC}/pgdist.py" create-version 1.0 -c "${PATH_CONFIG_1}"

#git create tag
log_git "add ."
git add .

log_git "commit -m 'test pgdist 1.0'"
git commit -m "test pgdist 1.0"

log_git "tag -a v1.0 -m 'test pgdist v1.0'"
git tag -a v1.0 -m "test pgdist v1.0"

log "test 1/2 finished"
