#### Install project:

So once you have prepared version of your project, you can try to install it.
It takes `my_project--1.0.0.sql` [install script](../../project_files/version.md) and loads it to *pg_database*.  

```
pgdist install <project> <dbname> [version]

Example:
$ pgdist install my_project project_pgdb 1.0.0 -C --directory ./sql_dist
CREATE DATABASE project_pgdb
CREATE ROLE my_beautiful_role NOLOGIN
Install my_project 1.0.0 part 1/2 to project_pgdb
Install my_project 1.0.0 part 2/2 to project_pgdb
Complete!
```

**args - required**:

- `project` - name of project you want to install

- `dbname` - name of database to install to

**args - optional**:

- `version` - version of project to install, if not specified, latest is taken instead

- `--directory` - path to directory which contains install/update sql scripts

- `-C` `--create` - *enable* - if database does not exist, create it

- `-U` `--username` - PG username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PG host

- `-p` `--port` - port that PG listens to
