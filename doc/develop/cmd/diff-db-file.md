### Diff db-file/file-db

Shows difference between installed project and selected file.

```
pgdist diff-db-file <PGCONN> <file>

Example:
$ pgdist diff-db-file root:password@my_server//pg_user:pg_password@/pg_database /path/to/your/SQL/file
```

Shows difference between selected file and installed project.

```
pgdist diff-file-db <file> <PGCONN>

Example:
$ pgdist diff-file-db /path/to/your/SQL/file root:password@my_server//pg_user:pg_password@/pg_database
```

**args - required**:

- `PGCONN` - connection to PG

- `file` - compare database with path to file

**args - optional**:

- `--diff-raw` - *enable* - compare raw SQL dumps

- `--no-clean` - *enable* - after loading project to database (parse purpose), it won´t clean it

- `--no-owner` - *enable* - don´t compare owners

- `--no-acl` - *enable* - don´t compare access privileges (grant/revoke commands)

- `--swap` - *enable* - swap data to compare

- `-w` `--ignore-all-space` - *enable* - ignore different whitespacing

- `--cache` - *enable* - cache remote dump for 4 hours

- `--pre-load` - path to file you want to load, load **before** current project

- `--post-load` - path to file you want to load, load **after** current project

- `--pre-remoted-load` - path to file you want to load, load **before** installed project

- `--post-remoted-load` - path to file you want to load, load **after** installed project

- `--pg_extractor` - *enable* - use PG extractor for PG dump, see more: https://github.com/omniti-labs/pg_extractor

- `--pg_extractor_basedir` - PG extractor dumps PG to this directory