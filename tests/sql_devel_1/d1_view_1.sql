CREATE OR REPLACE VIEW pgdist_test_schema.test_view_1 AS
SELECT tb1.id, tb2.test_table_1_id
FROM pgdist_test_schema.test_table_1 tb1
LEFT JOIN pgdist_test_schema.test_table_2 tb2
ON 1=1;