### List projects:

To show list of installed and available projects and their updates. If you want to show list of projects in some database without specifying project, use `-d` or `--dbname`.

```
pgdist list [project [dbname]]

Example:
$ pgdist list --directory ./sql_dist --showall

Available projects:
============================================================================
 project             version   all versions
 my_project          1.0.0     1.0.0
                               update: 1.0.0 -> 1.0.1
============================================================================

Installed projects:
============================================================================
 project             dbname              version   from      part parts
 my_project          project_pgdb        1.0.0     -         2    2
============================================================================
```

**args - optional**:

- `project` - show info about project

- `dbname` - show info about project in database

- `--directory` - path to directory which contains install/update sql scripts

- `--showall` - *enable* - show all versions of projects

- `-U` `--username` - PG username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PG host

- `-p` `--port` - port that PG listens to
