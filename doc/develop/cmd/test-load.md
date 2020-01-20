### Test load

It will try to load current state of your project to testing database (defined in [develop configuration file](../develop/config.md)).

```
pgdist test-load

Example:
$ pgdist test-load
load project my_project to test pg
dump structure and data from test pg
checking element owners

Project my_project was loaded successfully.
```

**args - optional**:

- `--no-clean` - *enable* - after loading project to database, it won´t clean it

- `--pre-load` - path to file you want to load BEFORE loading project to database

- `--post-load` - path to file you want to load AFTER loading project to database

- `--pg_extractor` - *enable* - use PG extractor for PG dump, see more: https://github.com/omniti-labs/pg_extractor

- `--pg_extractor_basedir` - PG extractor dumps PG to this directory
