# PGdist - PostgreSQL projects control system

## Develop part

Develop part is for usage on local compter. It cooperates with git.

### Develop directories

Source SQL files are in `sql`. Versions and updates scripts are in `sql_dist`.

```
├── sql
│   ├── pg_project.sql
│   └── project_schema
│       ├── functions
│       │   ├── function1.sql
│       │   ├── function2.sql
│       └── tables
│           └── table1.sql
└── sql_dist
    ├── my_project--1.0.0--1.1.0--p01.sql
    ├── my_project--1.1.0--p01.sql
    └── my_project--1.1.0--p02.sql
```

### pg_project.sql

File `sql/pg_project.sql` is project configuration file.

Parts can be defined in pg_project.sql. Part starts line `-- part`. Part can be `-- single_transaction` or `-- not single_transaction`.

### Config file

Local configuration file `~/.pgdist`:

```
[pgdist]
test_db: pgdist@sqltest/postgres
```

test_db is pgconn to testing postgres for `test-load` and `test-update`.

### Roles

Before install pgdist checks if roles in project exists in postgres. It check and change nologin/login option. If option password set, pgdist create in `/etc/lbox/postgresql/roles/` dir file `username` with content `PGPASSWORD=GENERATED_PASSWORD`.

### `pgdist init project [directory]`

Initialize pgdist project. Create `sql` and `sql_dist` directory. 

### `pgdist create-schema schema`

Create directory tree for schema. First level is schema name, second level is type of data type. Second level contains `*.sql ` files with SQL and DDL commands. Names of second level and files are arbitrary.

### `pgdist status`

show new files and removed files compared to pg_project.sql

### `pgdist add file1 [file2 ...]`

add files to pg_project.sql

### `pgdist rm file1 [file2 ...]`

removed files from pg_project.sql

### `pgdist test-load`

load project to testing postgres

### `pgdist create-version version [git_tag]`

create version files

### `pgdist create-update git_tag new-version`

create version files with differencies
- old-version - git tag
- new-version - version created by create-version

version file constainds different between old and new version. It have to be check and rewrite.

### `pgdist test-update git_tag new-version`

load old and new version and compare it and print diff
- old-version - git tag
- new-version - version created by create-version

### `pgdist diff-db pgconn [git_tag]`

diff existing database and project

### `pgdist role-list`

print roles in project

### `pgdist role-add name [nologin|login] [password]`

add role to project

### `pgdist role-change name [nologin|login] [password]`

change param on role

### `pgdist role-rm name`

remove role from project, not remove from databases



## Instalation part

Instalation part is for usage to install projects to database.

### `pgdist list [project [dbname]]`

show list of installed projects in database and sql files in project's directory

### `pgdist install project dbname [version]`

install project to database

### `pgdist update [project [dbname [version]]]`

update project

### `pgdist clean project [dbname]`

remove all info about project

### `pgdist set-version project version dbname`

force change version without run scripts

### `pgdist pgdist-update [dbname]`

update pgdist version in database
