| Develop options | Type | Description |
| --- | --- | --- |
| `-v, --verbose` | *increment* | increase output verbosity |
| `-?, --help` | *enable* | show help message and exit |
| `--git-diff` | *enable* | generate diff against git files |
| `--less` | *enable* | print output in less |
| `--noless` | *enable* | don´t print output in less |
| `--all` | *enable* | use all files |
| `-f, --force` | *enable* | if update file already exists, rewrite it |
| `-c, --config` | *specify* | configuration file |
| `--color` | *choose* | never, always or auto colorred output |
| `--swap` | *enable* | swap compare data |
| `--gitversion` | *specify* | use this as old version name to create update from (only name/file purposes) |
| `--no-owner` | *enable* | do not dump and compare ownership of objects |
| `--no-acl` | *enable* | do not dump and compare access privileges (grant/revoke commands |
| `--diff-raw` | *enable* | compare raw SQL dumps |
| `-w, --ignore-all-space` | *enable* | ignore all white space |
| `--no-clean` | *enable* | after loading project to database (parse purpose), it won´t clean it |
| `--cache` | *enable* | cache dump remote database for 4 hours |
| `--pg_extractor` | *enable* | dump by pg_extractor, compare by diff -r |
| `--pg_extractor_basedir` | *specify* | dump by pg_extractor do directory PG_EXTRACTOR_BASEDIR |
| `--pre-load-old` | *specify* | path to file you want to load **before old** project |
| `--pre-load-new` | *specify* | path to file you want to load **before new** project |
| `--post-load-old` | *specify* | path to file you want to load **after old** project |
| `--post-load-new` | *specify* | path to file you want to load **after new** project |
| `--pre-load` | *specify* | path to file you want to load, if `pre-load-old/new` is not specified, load **before both** projects |
| `--post-load` | *specify* | path to file you want to load, if `pre-load-old/new` is not specified, load **after both** projects |
| `--pre-remoted-load` | *specify* | SQL file to load before load remote dump |
| `--post-remoted-load` | *specify* | SQL file to load after project |
