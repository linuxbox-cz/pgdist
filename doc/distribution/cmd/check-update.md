#### Check update

After installation of your project, you may want to check for updates (you created obviously):

```
pgdist check-update [project [dbname [version]]]

Example:
$ pgdist check-update my_project --directory ./sql_dist

Project updates:
============================================================================
 project             dbname              update
 my_project          project_pgdb        1.0.0 -> 1.0.1
============================================================================
```

**args - optional**:

- `project` - search updates for project name

- `dbname` - search updates in specified database

- `version` - search for updates until version of project

- `--directory` - path to directory which contains install/update sql scripts

- `-U` `--username` - PG username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PG host

- `-p` `--port` - port that PG listens to
