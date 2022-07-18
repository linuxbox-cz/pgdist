#!/bin/bash

TEST_PART="devel_2 | "
log "test begin\n"

mkdir "${PATH_SEQUENCES}"
cd $PATH_TEST

#copy sql files to project directory
log "cp ${PATH_DEVEL_1}schema_1.sql ${PATH_SCHEMAS}/"
cp "${PATH_D2}/d2_schema_1.sql" "${PATH_SCHEMAS}/"

log "cp d2_table_1.sql ${PATH_TABLES}/"
cp "${PATH_D2}/d2_table_1.sql" "${PATH_TABLES}/"

log "cp d2_function_1.sql ${PATH_FUNCTIONS}/"
cp "${PATH_D2}/d2_function_1.sql" "${PATH_FUNCTIONS}/"

log "cp d2_index_1.sql ${PATH_INDEXES}/"
cp "${PATH_D2}/d2_index_1.sql" "$PATH_INDEXES/"

log "cp d2_trigger_1.sql ${PATH_TRIGGERS}/"
cp "${PATH_D2}/d2_trigger_1.sql" "${PATH_TRIGGERS}/"

log "cp d2_sequence_1.sql ${PATH_SEQUENCES}/"
cp "${PATH_D2}/d2_sequence_1.sql" "${PATH_SEQUENCES}/"

#change function
cd $PATH_SQL
echo "ALTER FUNCTION pgdist_test_schema.test_function_1() OWNER TO pgdist_test_role_1;" >> "${PATH_FUNCTIONS}/d1_function_1.sql"

#add files
log_pgdist "add ${PATH_SCHEMAS}/d2_schema_1.sql"
python3 "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_SCHEMAS}/d2_schema_1.sql" -c $PATH_CONFIG_DEV

log_pgdist "add ${PATH_TABLES}/d2_table_1.sql"
python3 "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_TABLES}/d2_table_1.sql" -c $PATH_CONFIG_DEV

log_pgdist "add ${PATH_INDEXES}/d2_index_1.sql"
python3 "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_INDEXES}/d2_index_1.sql" -c $PATH_CONFIG_DEV

log_pgdist "add ${PATH_FUNCTIONS}/d2_function_1.sql"
python3 "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_FUNCTIONS}/d2_function_1.sql" -c $PATH_CONFIG_DEV

log_pgdist "add ${PATH_TRIGGERS}/d2_trigger_1.sql"
python3 "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_TRIGGERS}/d2_trigger_1.sql" -c $PATH_CONFIG_DEV

log_pgdist "add ${PATH_SEQUENCES}/d2_sequence_1.sql"
python3 "${PATH_PGDIST_SRC}/pgdist.py" add "${PATH_SEQUENCES}/d2_sequence_1.sql" -c $PATH_CONFIG_DEV

#change roles
log_pgdist "role-list"
python3 "${PATH_PGDIST_SRC}/pgdist.py" role-list -c $PATH_CONFIG_DEV

log_pgdist "role-change pgdist_test_role_1 login password"
python3 "${PATH_PGDIST_SRC}/pgdist.py" role-change pgdist_test_role_1 login password -c $PATH_CONFIG_DEV

log_pgdist "role-change pgdist_test_role_2 nologin "
python3 "${PATH_PGDIST_SRC}/pgdist.py" role-change pgdist_test_role_2 nologin -c $PATH_CONFIG_DEV

log_pgdist "role-list"
python3 "${PATH_PGDIST_SRC}/pgdist.py" role-list -c $PATH_CONFIG_DEV

#change tables
log "ALTER TABLE test_table_1 OWNER TO pgdist_test_role_2"
sed -i '/ALTER TABLE/d' "$PATH_TABLES/d1_table_1.sql"
echo "ALTER TABLE pgdist_test_schema.test_table_1 OWNER TO pgdist_test_role_2;" >> "$PATH_TABLES/d1_table_1.sql"

log "ALTER TABLE test_table_2 RENAME data TO test_data"
sed -i 's/data/test_data/' "$PATH_TABLES/d1_table_2.sql"

log "ALTER TABLE test_table_2 OWNER TO pgdist_test_role_1"
echo "ALTER TABLE pgdist_test_schema.test_table_2 OWNER TO pgdist_test_role_1;" >> "$PATH_TABLES/d1_table_2.sql"

#change constraint
log "ALTER TABLE test_table_2 RENAME CONSTRAINT"
echo "ALTER TABLE pgdist_test_schema.test_table_2 ADD CONSTRAINT test_table_2_id_fkey FOREIGN KEY (test_table_1_id) REFERENCES pgdist_test_schema.test_table_1(id) ON DELETE CASCADE ON UPDATE CASCADE;" > "${PATH_CONSTRAINTS}/d1_constraint_1.sql"

#create update
log_pgdist "create-update v1.0 1.1"
python3 "${PATH_PGDIST_SRC}/pgdist.py" create-update v1.0 1.1 -c $PATH_CONFIG_DEV

#copy update file to install path
log "cp -a ${PATH_SQL_DIST}/. ${PATH_PGDIST_INSTALL}"
cp -a "${PATH_SQL_DIST}/." $PATH_PGDIST_INSTALL

#test update
log_pgdist "test-update v1.0 1.1"
cd $PATH_SQL
python3 "${PATH_PGDIST_SRC}/pgdist.py" test-update v1.0 1.1 -c $PATH_CONFIG_DEV

#git create tag
log_git "add ."
cd $PATH_PROJECT
git add .

log_git "commit -m 'test pgdist 1.1'"
git commit -m "test pgdist 1.1"

log_git "tag -a v1.1 -m 'test pgdist v1.1'"
git tag -a v1.1 -m "test pgdist v1.1"

log_git "tag -l"
git tag -l

#create version 1.1
log_pgdist "create-version 1.1.1 --version-length 2"
cd $PATH_SQL
python3 "${PATH_PGDIST_SRC}/pgdist.py" create-version 1.1.1 -c $PATH_CONFIG_DEV --version-length 2

log "test 2/3 finished"
