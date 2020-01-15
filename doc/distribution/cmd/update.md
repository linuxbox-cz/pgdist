#### Update

Now that you have checked for updates, you might want to update it with `my_project--1.0.1.sql`.
Takes `my_project--1.0.0--1.0.1.sql` [update script](../../project_files/update.md) and loads it to *pg_database*.  

If you don´t specify any parameter, PGdist will try to update each of your installed project.

```
pgdist update [project [dbname [version]]]

Example:
pgdist update my_project pg_database 1.0.1
```

**args - optional**:

- `project` - update project

- `dbname` - update project in database

- `version` - try to update project to most recent specified version of project

- `--directory` - path to directory which contains install/update sql scripts

- `-U` `--username` - PG username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PG host

- `-p` `--port` - port that PG listens to
