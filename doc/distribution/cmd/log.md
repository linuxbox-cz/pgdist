### Log

Prints PGdist history, that means when was something installed, updated or added roles etc..

```
pgdist log [project [dbname]]

Example:
$ pgdist log my_project postgres
```

**args - optional**:

- `project` - show info about project

- `dbname` - show info about projects from database

- `-U` `--username` - PG username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PG host

- `-p` `--port` - port that PG listens to
