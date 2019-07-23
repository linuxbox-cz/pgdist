CREATE TABLE pgdist_test_schema_3.test_table_1(
    id SERIAL NOT NULL,
    message TEXT,
    ts TIMESTAMPTZ
);

ALTER TABLE pgdist_test_schema_3.test_table_1 OWNER TO pgdist_test_role_2;
