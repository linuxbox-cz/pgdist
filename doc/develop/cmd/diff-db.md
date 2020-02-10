### Diff db

Show difference between your current project and installed project. Argument `--post-remoted-load` is very useful in case you create some hand-patch to unify versions.

```
pgdist diff-db <PGCONN> [git_tag]

Example:
$ pgdist diff-db postgres@/project_pgdb
dump remote
load dump to test pg
dump structure and data from test pg
load project my_project to test pg
dump structure and data from test pg
New tables:
		my_schema.customers

Table my_schema.products is different:
		+price integer
```

**args - required**:

- `PGCONN` - connection to PG

**args - optional**:

- `git_tag` - compare project git tag with database (if not specified, current file system version is taken instead)

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
