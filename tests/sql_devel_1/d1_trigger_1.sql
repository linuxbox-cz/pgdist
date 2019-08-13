CREATE TRIGGER test_nofity_1 AFTER INSERT OR UPDATE OR DELETE ON pgdist_test_schema.test_table_2 FOR EACH ROW EXECUTE PROCEDURE pgdist_test_schema.test_function_1();
