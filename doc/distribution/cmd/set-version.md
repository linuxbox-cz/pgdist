### Set version

Set version in pgdist info of your installed project by force.

```
pgdist set-version <project> <dbname> <version>

Example:
$ pgdist set-version my_project pg_database 1.0.2
```

**args - required**:

- `project` - change info about project

- `dbname` - change info about project in database

- `version` - change info about project´s version

**args - optional**:

- `-U` `--username` - PG username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PG host

- `-p` `--port` - port that PG listens to
