#### Get version

Shows version of specified project.

```
pgdist get-version <project> <dbname>

Example:
$ pgdist get-version my_project pg_database
```

**args - required**:

- `project` - get version of project

- `dbname` - get version of project in database

**args - optional**:

- `-U` `--username` - PG username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PG host

- `-p` `--port` - port that PG listens to
