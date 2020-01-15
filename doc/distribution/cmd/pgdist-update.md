### PGdist update

Update pgdist version in database. If not specified, update all database where is PGdist installed.

```
pgdist [dbname]

Example:
$ pgdist postgres
```

**args - optional**:

- `dbname` - database where should be PGdist updated

- `-U` `--username` - PG username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PG host

- `-p` `--port` - port that PG listens to
