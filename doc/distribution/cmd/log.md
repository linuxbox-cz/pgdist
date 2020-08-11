### Log

Prints PGdist history, that means when was something installed, updated or added roles etc..

```
pgdist log [project [dbname]]

Example:
$ pgdist log TIME                DBNAME                     PROJECT           VERSION COMMENT
2019-11-29 01:11:15 project_pgdb               my_project        1.0.0   CREATE ROLE my_beautiful_role nologin
2019-11-29 01:11:15 project_pgdb               my_project        1.0.0   installed new version 1.0.0, part 1/2
2019-11-29 01:11:15 project_pgdb               my_project        1.0.0   installed new version 1.0.0, part 2/2
2019-11-29 02:11:31 project_pgdb               my_project        1.0.1   updated from version 1.0.1 to 1.0.0, part 1/1
```

**args - optional**:

- `project` - show info about project

- `dbname` - show info about projects from database

- `-U` `--username` - PG username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PG host

- `-p` `--port` - port that PG listens to
