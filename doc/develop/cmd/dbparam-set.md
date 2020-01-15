#### DB parameters set

Before you load your project to database, you may want to set some things before creating database.

```
pgdist dbparam-set <dbparam>

Example:
pgdist dbparam-set OWNER my_beatufil_role ENCODING utf8 CONNECTION LIMIT -1
```

**args - required**:

- `dbparam` - parameters to create database with, see more: https://www.postgresql.org/docs/current/sql-createdatabase.html, PGdist will literally take it and put it at the end of command
