#### Rm

Command for removing files from [project config. file](../../project_files/config.md). If you want to delete the file, you have to do it yourself.

```
pgdist rm [file...]

Example:
$ pgdist rm /path/to/your/SQL/file_1 /path/to/your/SQL/file_2
```

**args - required**:

- `file` - *multiple* - path to file you want to add to your project

**args - optional**:

- `--all` - *enable* - removes all *REMOVED FILE* from your project, if used, `file` argument is not required
