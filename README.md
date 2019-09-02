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

Add role to project:

```
pgdist role-add My_beatufiul_role login password
```

* The above command creates role *My_beautiful_role* with ability to **login**, creates **password** and stores it to directory defined either by you with `--directory` OR in path setted in configuration file

* If you want to create role without *password*, just don't add it, or if you want to create role without login, use `nologin`

Change settings for your role in project:

```
pgdist role-change My_beautiful_role nologin
```

* You don't like your role anymore? You can change its settings by above command.

Remove role from project:

```
pgdist role-rm My_beautiful_role
```

* Do you hate your role so much, you want to delete it? Yep, above command.

**NOTICE** - If you already made some role in your database, this will not help you to remove it from database.

List roles in project:

```
pgdist role-list
```

* Lists all roles in your project



### Project file managment

Add file to project:

* Move your SQL file to the correct directory (`table.sql` to `tables`, `schema.sql` to `schema`, etc.)

```
pgdist add /path/to/your/SQL/file_1 /path/to/your/SQL/file_2
```

**NOTICE** - This command will ONLY remove it from `pg_project.sql`, if you want to delete the file, you have to do it yourself.

Remove file from project:

* There's three ways you can do it:

	1. Delete line with path to your file you want to delete from `pg_project.sql`

	2. Use pgdist command `rm`

	3. You can use command `status` to show difference in your project folder and than remove deleted files from your project by adding parameter `--manage-files`

```
pgdist rm /path/to/your/SQL/file_1 /path/to/your/SQL/file_2
```

Show status of project files:

```
pgdist status
```

* Shows files, which are in project directory, but are not added to project as NEW FILE

* Shows files, which are added to project, but were not found in project directory as REMOVED FILE

* If you want to remove deleted files from your project, add parameter `--manage-files`:

**Recommendations:**

1. Add your files to your project in the order as if you would be addding them to your database directly (this will ensure, that you won't have to adjust import file order in `pg_project.sql`). **Example**: first you would add all your `schema.sql` into your project then everything else that depends on it.

2. As the above point points out to file order, try to adjust or split your SQL dependencies in the order, so you don't have to adjust your `version.sql` file.

3. Data will be added only in file created by `create-version`.



### Project reuqires

If your project has dependency on some other project, you can add a require on other project:

```
pgdist require-add My_Other_Project https://url_or_ssh_to_your_other_project branch_name
```

**NOTICE** - Above command works only when used before `create-version`.

Well if you changed your mind or your project just does not have dependency on other project, you can remove it:

```
pgdist require-rm My_Other_Project
```



### DB-parameters

Before you load your project to database, you may want to set some things before crerating database:

```
pgdist dbparam-set OWNER My_beatufil_role ENCODING utf8 CONNECTION LIMIT -1
```

* Parameters are described here: https://www.postgresql.org/docs/9.6/sql-createdatabase.html, PGdist will literally take it and put it at the end of command

And you will also want to list them:

```
pgdist dbparam-get
```



### Versions

Once you're satisfied with your project, you can try to load it to database, to test, if it would even pass without errors.

```
pgdist test-load
```

* It will try to load current state of your project.

**NOTICE** - This command requires configuration file to have setted *PGCONN* in section *pgdist*.

If your `test-load` ended successfully, you may create version.  

Create version of your project:

```
pgdist create-version 1.0.0 v1.0.0
```

* First parameter defines **PROJECT** version, second one is **GIT-TAG**.

* Git tag is not required, use it only if you want to create version from specified git tag.

* Those parameters don´t have to be same, so if you have like git tag v6.7.9, and you want to create project version 1.0.0, you can do so.

* The above command creates new file `My_Project--1.0.0.sql` in your `sql_dist` folder.

**NOTICE** - Something can be added only when using this command, like `require-add` or `data`

You already made your first version and forgot to add something? Don't worry, we got you.

Create update from your version:

	```
	pgdist create-update v1.0.0 1.0.1
	```

	* First parameter is already mentioned git tag, pgdist will create update for given git tag.

	* Second parameter is NEW project version.

	* This command creates new file `My_Project--1.0.0--1.0.1.sql` in your `sql_dist` folder.

Test update of your project:

```
pgdist test-update v1.0.0 1.0.1
```

* First paramater, again, git tag.

* Second parameter project version.

* Loads git tag version of your project to test database, then tries to use your update on it.



### Project installation

So once you have prepared version of your project, you can try to install it.

```
pgdist install My_Project pg_database 1.0.0
```

* If you want PGdist to create the database, add `--create`

* Takes `My_Project--1.0.0.sql` and loads it to *pg_database*.

* If you don´t specify project version, latest is taken.

After installation of your project, you may want to check for updates (you created obviously):

```
pgdist check-update My_Project pg_database 1.0.0
```

* First parameter is your project name
* Second parameter is database that it is installed in
* Third parameter is from what version you want to find udpates

Now that you have checked for updates, you might want to update it with `My_Project--1.0.1.sql`.

```
pgdist update My_Project pg_database 1.0.1
```

* Takes `My_Project--1.0.0--1.0.1.sql` and loads it to *pg_database*.

* If you don´t specify any parameter, pgdist will try to update each of your installed project.

To show list of installed projects:

```
pgdist list My_Project pg_database
```

* Shows (if it is installed of course) info about My_Project in pg_database

If you want to remove info about your project:

```
pgdist clean My_Project pg_database
```



### Project diff

Let's say you've installed some version of your project to your servers. Now you made a lot of changes in your project and you want to see the diffrence.  

If you've added some `data.sql` to your project and want to compare them:

```
pgdist data-add some_table table_column_1 table_column_2
```

* PGdist will add this table to his list of tables data to compare with.

* As you can see, you may also specify which columns you want to compare.

Remove data from comparing:

```
pgdist data-rm some_table
```

* Removes *some_table* from pgdist list of tables data to compare

To see what table data you have added/removed:

```
pgdist data-list
```

* Shows list from tables data to compare

Show difference between your current project and installed project:

```
pgdist diff-db root:password@my_server//pg_user:pg_password@/pg_database v1.0.0
```

* Specify *PGCONN* and git tag, pgdist will then dump database from *PGCONN* and compare it with your project

Show difference between selected file and installed project:

```
pgdist diff-db-file root:password@my_server//pg_user:pg_password@/pg_database /path/to/your/SQL/file
```

* Dumps remote database and compare it with you file

**NOTICE** - If you want to show differences the opposite way, use `diff-file-db` and swap arguments

Set version to your project by force:

```
pgdist set-version My_Project pg_database 1.0.2
```



## Authors

* Marian Krucina LinuxBox.cz

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE (Version 2) - see the COPYING file for details
