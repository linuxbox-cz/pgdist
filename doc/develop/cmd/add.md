#### Add

To add file to your project, move it to the `sql` directory (if you are using your directory structure), or move it to the correct directory (`table.sql` to `tables`, `schema.sql` to `schema`, etc.) and run command below.

```
pgdist add [file...]

Example:
$ pgdist add my_schema/schema/schema.sql my_schema/tables/products.sql
Added to project:
	my_schema/schema/schema.sql
Added to project:
	my_schema/tables/products.sql

If you need, change order of files in project file sql/pg_project.sql
```

**args - required**:

- `file` - *multiple* - path to file you want to add to your project

**args - optional**:

- `--all` - *enable* - adds all *NEW FILE* to your project, if used, `file` argument is not required
