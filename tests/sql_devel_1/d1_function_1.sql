CREATE OR REPLACE FUNCTION pgdist_test_schema.test_function_1()
    RETURNS TRIGGER
    LANGUAGE plpgsql
AS $function$
DECLARE
    x TEXT;
BEGIN
    x := "test data";
    UPDATE pgdist_test_schema.test_table_1 SET data=x, ts=NOW();
    RETURN trigger;
END;
$function$;
