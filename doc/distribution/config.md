### Distribution config file

Configuration file is located at `/etc/pgdist.conf`.

```
[pgdist]
installation_path = /usr/share/pgdist/install
password_path = /etc/lbox/postgresql/roles
pguser = postgres
pgdatabase = postgres
pghost = localhost
pgport = 5432
```

- `installation_path` - path to version/updates scripts

- `password_path` - path to roles passwords (created by PGdist)

- `pguser` - default PG user to connect with

- `pgdatabase` - *optional* - name of database to connect to

- `pghost` - *optional* - PG host

- `pgport` - *optional* - port that PG listens to

[**BACK TO DOCS**](../doc.md)  
[**BACK TO TUTORIAL**](../tutorial.md)  
