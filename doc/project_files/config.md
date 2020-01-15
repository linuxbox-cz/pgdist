### Project config file

File `sql/pg_project.sql` is project configuration file. It contains header with some info and settings (project name, roles, table_data, parts, etc.) for commands [create-version](../develop/cmd/create-version.md) and [create-update](../develop/cmd/create-update.md). It also contains paths to source files.  

```
-- pgdist project
-- name: my_project

-- table_data: my_schema.table

-- end header_data

-- part
-- single_transaction

\ir my_schema/schema/schema.sql

-- part
-- not single_transaction

\ir my_schema/tables/some_table.sql
```
