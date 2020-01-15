### Develop config file

Configuration file is located at `~/.pgdist`. It is used when test loading projects to database.

```
[pgdist]
test_db: pgdist@sqltest/postgres
```

- `test_db` - PG connection to testing PostgreSQL database.

#### PGCONN

It defines ssh connection (**not required**) + connection URI.  
Please use connection URI **without** `postgresql://` string.  
If you choose to use ssh connection, it is highly recommended to set up **ssh-key**.  
See more about connection URI: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING.  

```
host_user@host//pg_user:pg_password@pg_host:pg_port/pg_database?pg_params
```

**Examples**  

Simple PGCONN might look like this:  

```
localhost/test_database
postgres@/test_database
localhost//postgres@/
```

Below PGCONN will define ssh connection to *my_server* with user *root* on port *8089*, then open postgres connection with PG user *postgres*, password *PASSWORD*, PG host *localhost*, listening port *5042*, database *test_database* and connection timeout *10 seconds*.  

```
root@my_server:8089//postgres:PASSWORD@localhost:5042/test_database?connection_timetout=10
```
