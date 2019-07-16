CREATE OR REPLACE FUNCTION pgdist_schema_test.test_function_1()
    RETURNS BOOLEAN
    LANGUAGE plpgsql
AS $function$
DECLARE
    x TEXT;
BEGIN
    x := "test message";
    INSERT INTO pgdist_schema_test.test_table_1(message, ts) VALUES (x, NOW());
    RETURN true;
END;
$function$;