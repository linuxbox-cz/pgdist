### Role list

Before PGdist installs project into the databse, it will check if roles defined in project exists in database. It checks roles and changes nologin/login option. If option password is set, PGdist will create file `username` in path defined in [distribution config file](../../distribution/config.md) with content `PGPASSWORD=GENERATED_PASSWORD`.

```
$ pgdist role-list
```
