### Clean

If you want to remove info (showed by `list`) about your project:

```
pgdist clean <project> [pg_database]

Example:
$ pgdist clean My_Project postgres
```

**args - required**:

- `project` - clean info about project

**args - optional**:

- `dbname` - clean project from database

- `-U` `--username` - PG username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PG host

- `-p` `--port` - port that PG listens to
