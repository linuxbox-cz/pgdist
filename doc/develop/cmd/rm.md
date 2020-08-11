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
