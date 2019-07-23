CREATE TABLE pgdist_test_schema.test_table_1(
    id SERIAL NOT NULL UNIQUE,
    message TEXT,
    data TEXT,
    ts TIMESTAMPTZ
);

ALTER TABLE pgdist_test_schema.test_table_1 OWNER TO pgdist_test_role_1;
