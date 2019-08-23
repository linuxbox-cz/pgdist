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

Local configuration file is `~/.pgdist`:

```
[pgdist]
test_db: pgdist@sqltest/postgres
```

test_db is pgconn to testing postgres for `test-load` and `test-update`.

### Roles

Before install pgdist checks if roles in project exists in postgres. It checks and changes nologin/login option. If option password is set, pgdist will create in `/etc/lbox/postgresql/roles/` dir file `username` with content `PGPASSWORD=GENERATED_PASSWORD`.


### Help
```
PGdist - distributes PotgreSQL functions, tables, etc...
PGdist Devel - develop PostgreSQL project

    init PROJECT [DIRECTORY] - initialize pgdist project
    create-schema SCHEMA - create new schema directory
    status - show new (not added) files and removed files compared to pg_project.sql
    add FILE1 [FILE2 ...] - add files to pg_project.sql
    rm FILE1 [FILE2 ...] - remove files from pg_project.sql

    test-load - load project to testing postgres
    create-version VERSION [GIT_TAG] - create version files
    create-update GIT_TAG NEW_VERSION - create update files with differencies
                                          - GIT_TAG - old version tag
                                          - NEW_VERSION - new version
    test-update GIT_TAG NEW_VERSION - load old and new version and compare it
                                          - GIT_TAG - old version tag
                                          - NEW_VERSION - new version

    diff-db PGCONN [GIT_TAG] - diff project and database
    diff-db-file PGCONN FILE - diff file and database
    diff-file-db FILE PGCONN - diff database and file

    role-list - print roles in project
    role-add NAME [login|nologin] [password] - add role to project
    role-change NAME [login|nologin] [password] - change role
    role-rm NAME - remove role from project, not remove from databases

    require-add PROJECT GIT GIT_TREE_ISH - add require to another project
    require-rm PROJECT - remove require to another project

    dbparam-set [PARAM [...]] - parameters with create a database (e.g.: OWNER lbadmin ...)
    dbparam-get - print parameters to create a database

    data-add TABLE [COLUMN1 [...]] - add table to compare data
    data-rm TABLE - remove table to compare data
    data-list - list table of data compare

PGdist Server - manage projects in PostgreSQL database

    list [PROJECT [DBNAME]] - show list of installed projects in databases
    install PROJECT DBNAME [VERSION] - install project to database
    check-update [PROJECT [DBNAME [VERSION]]] - check update project
    update [PROJECT [DBNAME [VERSION]]] - update project
    clean PROJECT [DBNAME] - remove all info about project
    set-version PROJECT DBNAME VERSION - force change version without run scripts
    pgdist-update [DBNAME] - update pgdist version in database

PGCONN - ssh connection + connection URI, see:
    https://www.postgresql.org/docs/current/static/libpq-connect.html#LIBPQ-CONNSTRING
    without string 'postgresql://'
    examples:
        localhost/mydb - connect to mydb
        root@server//user@/mydb - connect to server via ssh and next connect to postgres as user into mydb

Configuration:
    connection to testing database in file "~/.pgdist" (or ".pgdist" in project path) with content:
        [pgdist]
        test_db: user@host/dbname

        test_db - PGCONN to testing postgres, user has to create databases and users
```

## Tutorial

### Creating project directory

1. Init your project with:
```
pgdist init My_Project /path/to/my/project
```

* That creates directory structure as follows:
```
├── sql
│   └── pg_project.sql
└── sql_dist
```

2. Init schema directory:
```
pgdist create-schema my_schema
```

* That creates schema directory to your project:
```
├── sql
│   ├── pg_project.sql
│   └── my_schema
│       ├── constraints
│       ├── data
│       ├── extensions
│       ├── functions
│       ├── grants
│       ├── indexes
│       ├── schema
│       ├── tables
│       ├── triggers
│       ├── types
│       ├── views
└── sql_dist
```
* **NOTICE** - This will NOT create any *my_schema.sql* in my_schema folder.

### Project file managment

1. Add file to project:
* Move your SQL file to the correct directory (`table.sql` to `tables`, `schema.sql` to `schema`, etc.)
```
pgdist add /path/to/your/SQL/file_1 /path/to/your/SQL/file_2
```
* **NOTICE** - This command will ONLY remove it from `pg_project.sql`, if you want to delete the file, use argument `--manage-file`

2. Remove file from project:
* There's two ways you can do it:
	1. Delete line with path to your file you want to delete from *pg_project.sql*
	2. Use pgdist command rm
```
pgdist rm /path/to/your/SQL/file_1 /path/to/your/SQL/file_2
```

3. Show status of project files:


**Recommendation:**
1. Add your files to your project in the order as if you would be addding them to your database directly (this will ensure, that you won't have to adjust import file order in `pg_project.sql`).
2. As the above point points out to file order, try to adjust or split your SQL dependencies in the order, so you don't have to adjust your `version.sql` file.

## Authors

* Marian Krucina LinuxBox.cz

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE (Version 2) - see the COPYING file for details
