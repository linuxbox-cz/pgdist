### Create update

This command creates new file `my_project--1.0.0--1.0.1.sql` in your `sql_dist` folder.  
If `part_count` is specified, PGdist will create specified number of parts with headers and it will put all update-sql in **first part**, it is up to you to divide your sql to parts.  

```
pgdist create-update <git_tag> <new_version> [part_count]

Example:
$ pgdist create-update v1.0.0 1.0.1
load project my_project to test pg
dump structure and data from test pg
load project my_project to test pg
dump structure and data from test pg
Edit created file: sql_dist/my_project--1.0.0--1.0.1.sql
and test it by 'pgdist test-update v1.0.0 1.0.1'
```

**args - required**:

- `git_tag` - create update from git tag

- `new_version` - new version of project

**args - optional**:

- `part_count` - define how many parts should PGdist create

- `-f` `--force` - *enable* - if update file already exists, rewrite it

- `--gitversion` - use this as old version name to create update from (only name/file purposes)

- `--no-clean` - *enable* - after loading project to database (parse purpose), it won´t clean it

- `--pre-load` - path to file you want to load, if `pre-load-old/new` is not specified, load **before both** projects

- `--pre-load-old` - path to file you want to load **before old** project

- `--pre-load-new` - path to file you want to load **before new** project

- `--post-load` - path to file you want to load, if `pre-load-old/new` is not specified, load **after both** projects

- `--post-load-old` - path to file you want to load **after old** project

- `--post-load-new` - path to file you want to load **after new** project
