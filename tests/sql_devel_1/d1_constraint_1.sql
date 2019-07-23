ALTER TABLE pgdist_test_schema.test_table_2 ADD CONSTRAINT test_table_2_id_fkey FOREIGN KEY (test_table_1_id) REFERENCES pgdist_test_schema.test_table_1(id) ON UPDATE CASCADE;
