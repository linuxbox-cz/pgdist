CREATE TRIGGER test_nofity_2 AFTER INSERT OR UPDATE OR DELETE ON pgdist_test_schema_3.test_table_1 FOR EACH ROW EXECUTE FUNCTION pgdist_test_schema.test_function_1();
