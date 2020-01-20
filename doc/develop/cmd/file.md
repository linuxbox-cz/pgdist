### Status

Shows files, which are in your project directory.

- Files in project´s directory which have not been added to project: *NEW FILE*.

- Files in which are added to project but are not in project´s directory: *REMOVED FILE*.

```
pgdist status

Example:
$ pgdist status
PROJECT: my_project
NEW FILE: sql/my_schema/schema/schema.sql
REMOVED FILE: sql/my_schema/tables/products.sql
```



### Add

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



### Rm

Command for removing files from [project config. file](../../project_files/config.md). If you want to delete the file, you have to do it yourself.

```
pgdist rm [file...]

Example:
$ pgdist rm my_schema/schema/schema.sql my_schema/tables/products.sql
Removed from project:
	my_schema/schema/schema.sql
Removed from project:
	my_schema/tables/products.sql
```

**args - required**:

- `file` - *multiple* - path to file you want to add to your project

**args - optional**:

- `--all` - *enable* - removes all *REMOVED FILE* from your project, if used, `file` argument is not required
