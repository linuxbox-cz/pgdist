#### Add

To add file to your project, move it to the `sql` directory (if you are using your directory structure), or move it to the correct directory (`table.sql` to `tables`, `schema.sql` to `schema`, etc.) and run command below.

```
pgdist add [file...]

Example:
$ pgdist add /path/to/your/SQL/file_1 /path/to/your/SQL/file_2
```

**args - required**:

- `file` - *multiple* - path to file you want to add to your project

**args - optional**:

- `--all` - *enable* - adds all *NEW FILE* to your project, if used, `file` argument is not required
