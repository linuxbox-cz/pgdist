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
        server_username@server_name//pg_user@/pg_database - connect to server_name via ssh and next connect to postgres as pg_user into pg_database

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
		**NOTICE** - This will NOT create any *my_schema.sql* in my_schema folder.



### Roles
1. Add role to project:
	```
	pgdist role-add My_beatufiul_role login password
	```
	* The above command creates role *My_beautiful_role* with ability to **login**, creates **password** and stores it to directory defined either by you with `--directory` OR in path setted in configuration file
	* If you want to create role without *password*, just don't add it, or if you want to create role without login, use `nologin`
2. Change settings for your role in project:
	```
	pgdist role-change My_beautiful_role nologin
	```
	* You don't like your role anymore? You can change its settings by above command.
3. Remove role from project:
	```
	pgdist role-rm My_beautiful_role
	```
	* Do you hate your role so much, you want to delete it? Yep, above command.
	**NOTICE** - If you already made some role in your database, this will not help you to remove it from database.

### Project file managment
1. Add file to project:
	* Move your SQL file to the correct directory (`table.sql` to `tables`, `schema.sql` to `schema`, etc.)
	```
	pgdist add /path/to/your/SQL/file_1 /path/to/your/SQL/file_2
	```
	**NOTICE** - This command will ONLY remove it from `pg_project.sql`, if you want to delete the file, you have to do it yourself.

2. Remove file from project:
	* There's three ways you can do it:
		1. Delete line with path to your file you want to delete from `pg_project.sql`
		2. Use pgdist command `rm`
		3. You can use command `status` to show difference in your project folder and than remove deleted files from your project by adding parameter `--manage-files`
	```
	pgdist rm /path/to/your/SQL/file_1 /path/to/your/SQL/file_2
	```

3. Show status of project files:
	* If you want to remove deleted files from your project, add parameter `--manage-files`
		```
		pgdist status
		```
**Recommendations:**
1. Add your files to your project in the order as if you would be addding them to your database directly (this will ensure, that you won't have to adjust import file order in `pg_project.sql`).
**Example**: first you would add all your `schema.sql` into your project then everything else that depends on it
2. As the above point points out to file order, try to adjust or split your SQL dependencies in the order, so you don't have to adjust your `version.sql` file.



### Versions
* Once you're satisfied with your project, you can try to load it to database, to test, if it would even pass without errors.
	1. Try load your project to database:
		```
		pgdist test-load
		```
		* It will try to load current state of your project
		**NOTICE** - This command requires configuration file to have setted *PGCONN* in section *pgdist*

* If your `test-load` ended successfully, you may create version
	2. Create version of your project:
		```
		pgdist create-version 1.0.0 v1.0.0
		```
		* First parameter defines **PROJECT** version, second one is **GIT-TAG**
		* Git tag is not required, use it only if you want to create version from specified git tag
		* Those parameters don´t have to be same, so if you have like git tag v6.7.9, and you want to create project version 1.0.0, you can do so
		* The above command creates new file `My_Project--1.0.0.sql` in your `sql_dist` folder
* You already made your first version and forgot to add something? Don't worry, we got you.
	3. Create update from your version:
		```
		pgdist create-update v1.0.0 1.0.1
		```
		* First parameter is already mentioned git tag, pgdist will create update for given git tag.
		* Second parameter is NEW project version
		* This command creates new file `My_Project--1.0.0--1.0.1.sql` in your `sql_dist` folder
* You made create-update and you want to know, if you can load it to database?
	4. Test update of your project:
		```
		pgdist test-update v1.0.0 1.0.1
		```
		* First paramater, again, git tag
		* Second parameter project version
		* Loads git tag version of your project to test database, then tries to use your update on it



## Project installation
* So you have prepared version of your project and now want to load it to database?
	1. Install project to database:
		```
		pgdist install My_Project pg_database 1.0.0
		```
		* Takes My_Project--1.0.0.sql and loads it to *pg_database*
		* If you don´t specify project, version, latest is taken


## Authors

* Marian Krucina LinuxBox.cz

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE (Version 2) - see the COPYING file for details
