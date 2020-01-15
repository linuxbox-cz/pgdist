### Test update:

Loads git tag version of your project to test database (defined in [develop configuration file](../../develop/config.md)), then tries to use your update on it and in the end, it will print diff between old and new version.

```
pgdist test-update <git_tag> <version>

Example:
pgdist test-update v1.0.0 1.0.1
```

**args - required**:

- `git_tag` - test update on git tag version

- `version` - version of project

**args - optional**:

- `--gitversion` - use this as old version name to test update from (only name/file purposes)

- `--no-clean` - *enable* - after loading project to database (parse purpose), it won´t clean it

- `--pre-load` - path to file you want to load, if `pre-load-old/new` is not specified, load **before both** projects

- `--pre-load-old` - path to file you want to load **before old** project

- `--pre-load-new` - path to file you want to load **before new** project

- `--post-load` - path to file you want to load, if `pre-load-old/new` is not specified, load **after both** projects

- `--post-load-old` - path to file you want to load **after old** project

- `--post-load-new` - path to file you want to load **after new** project

- `--pg_extractor` - *enable* - use PG extractor for PG dump, see more: https://github.com/omniti-labs/pg_extractor

- `--pg_extractor_basedir` - PG extractor dumps PG to this directory
