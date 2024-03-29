### Create version

Below command creates new file `my_project--1.0.0.sql` in your `sql_dist` folder.  
In case your project is made from multiple parts `create-version` will make **new** [`version file`](../../project_files/version.md) for each part.

**NOTICE** - Something can be added only when using this command, like `require-add` or *table data*.

```
pgdist create-version <version> [git_tag]

Example:
$ pgdist create-version 1.0.0 v1.0.0
Created file: my_project--1.0.0--p01.sql
Created file: my_project--1.0.0--p02.sql

$ pgdist create-version 1.0.0.1 v1.0.0.1 --version-length 3
Created file: my_project--1.0.0--p01.sql
Created file: my_project--1.0.0--p02.sql
```

**args - required**:

- `version` - version of project

**args - optional**:

- `git_tag` - create version from git tag (if not specified, current file system version is taken instead)

- `--version-length` - count of version numbers which should pgdist generate during create-version eg. length: 3, version: 1.2.3; length: 2, version: 1.2

- `-f` `--force` - *enable* - if version file already exists, rewrite it
