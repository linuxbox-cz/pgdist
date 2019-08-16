--
-- pgdist project
--
-- name: pgdist_test_project_2
-- version: 1.0
--
-- part: 1
-- single_transaction
-- end header
--


--
-- sqldist file: pgdist_test_schema_2/schema/schema_1.sql
--

CREATE SCHEMA pgdist_test_schema_2;
;-- end sqldist file

--
-- sqldist file: pgdist_test_schema_2/tables/table_1.sql
--

CREATE TABLE pgdist_test_schema_2.test_table_1(
    id SERIAL NOT NULL,
    data TEXT,
    test_table_1_id INTEGER NOT NULL,
    ts TIMESTAMPTZ
);
;-- end sqldist file

--
-- sqldist file: pgdist_test_schema_2/tables/table_2.sql
--

CREATE TABLE pgdist_test_schema_2.test_table_2(
    id SERIAL NOT NULL,
    message TEXT
);
;-- end sqldist file

--
-- end sqldist project
--
