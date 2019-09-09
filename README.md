# PGdist - PostgreSQL projects control system

## Content

* [Description](#description-▲)

	* [Develop config file](#develop-config-file-▲)

		* [PGCONN](#pgconn-▲)

	* [Distribution config file](#distribution-config-file-▲)

* [Tutorial](#tutorial-▲)

	* [Create project](#create-project-▲)

	* [Roles](#roles-▲)

	* [File management](#file-management-▲)

	* [Requires](#requires-▲)

	* [DB parameters](#db-parameters-▲)

	* [Versions](#versions-▲)

	* [Project distribution](#project-distribution-▲)

	* [Compare projects](#compare-projects-▲)

## Description [▲](#content)

Let me introduce our project PGdist, used for postgres projects management from development to production.
URL: https://github.com/linuxbox-cz/pgdist

PGdist can:
- manage source files, collaborating with Git
- test project installation in postgres
- help to create update scripts and test it for mistakes
- display project‘s diff and existing database structure
- watch for proper role creation in database
- allow dependency settings
- compare data in tables
- make installations and updates on production server (inc. roles, dependencies)
- allow to split install and update scripts to parts, intended to be or not to be done in particular transaction
- show diffs in structured and colored mode

PGdist requires:
- Postgres
- Git

The main motivation was standardization of many projects in pg.  
PGdist will help us to create new version and its rpm package.  
On the other hand, it will install or update the project from rpm on production server.  
PGdist also can compare very old installation (and possible hand-made changes) and help us to prepare update script to standard version.  
PGdist also requires a little bit of **DIY - do it yourself**.  

**Develop part** - It is for usage on local computer. It cooperates with git.  

**Distribution part** - It is for usage on production server.

### Develop config file [▲](#content)

Configuration file is located at `~/.pgdist`.

```
[pgdist]
test_db: pgdist@sqltest/postgres
```

- `test_db` - PG connection to testing postgres database.

#### PGCONN [▲](#content)

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

Below PGCONN will define ssh connection to *my_server* with user *root*, then open postgres connection with PG user *postgres*, password *PASSWORD*, PG host *localhost*, listening port *5042*, database *test_database* and connection timeout *10 seconds*.  

```
root@my_server//postgres:PASSWORD@localhost:5042/test_database?connection_timetout=10
```

### Distribution config file [▲](#content)

Configuration file is located at `/etc/pgdist.conf`.

```
[pgdist]
installation_path = /usr/share/pgdist/install
password_path = /etc/lbox/postgresql/roles
pguser = postgres
pgdatabase = pg_database
pghost = localhost
pgport = 5042
```

- `installation_path` - path to version/updates scripts  

- `password_path` - path to roles passwords  

- `pguser` - default PG user to connect with  

- `pgdatabase` - *optional* - name of database to connect to  

- `pghost` - *optional* - PG host  

- `pgport` - *optional* - port that PG listens to  



## Tutorial [▲](#content)

### Create project [▲](#content)

#### Init your project with:

```
pgdist init My_Project [/path/to/my/project]
```

**args - required**:

- `project` - name of your desired project

**args - optional**:

- `path` - path to folder to create project in

That creates directory structure as follows:

```
├── sql
│   └── pg_project.sql
└── sql_dist
```

Version and update scripts are in `sql_dist` folder.

#### Project configuration file

File `sql/pg_project.sql` is project configuration file. It contains header with some info and settings (project name, roles, table_data, parts, etc.) for command `create-version/update`. It also contains paths to source files.  

```
-- pgdist project
-- name: My_Project

-- table_data: my_schema.table

-- end header_data

-- part
-- single_transaction

\ir my_schema/schema/schema.sql

-- part
-- not single_transaction

\ir my_schema/tables/some_table.sql

```

**NOTICE** - Each part has its own header defining which transaction to use, parts in `pg_project.sql` are only used with `create-version` command. See more about parts in section [Versions](#versions-▲)).

#### Init schema directory:

```
pgdist create-schema my_schema
```

**args - required**:

- `schema` - name of your desired schema

That creates schema directory to your project:

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

Source SQL files are in `sql/your_schema` folder.  

**NOTICE** - This will NOT create any *my_schema.sql* in my_schema folder. If this directory structure does not fit your demands, you can use any other, this structure is only recommended.



### Roles [▲](#content)

#### Add role to project:

```
pgdist role-add My_beautiful_role [login | nologin] [password]
```

**args - required**:

- `name` - name of your role

**args - optional**:

- `login` - *choose* - *login* for enabling login for your role, otherwise *nologin*

- `password` - *choose* - *password* if you want PGdist to create and set password for your role when installing/updating your project

The above command creates role *My_beautiful_role* with ability to **login** and when installing PGdist creates **password** and stores it to directory defined in *Distribution* configuration file.  

#### Change settings for your role in project:

```
pgdist role-change My_beautiful_role [login | nologin] [password]
```

**args - required**:

- `name` - name of role you want to change

**args - optional**:

- `login` - *choose* - *login* for enabling login for your role, otherwise *nologin*

- `password` - *choose* - *password* if you want PGdist to create and set password for your role when installing/updating your project

You don´t like your role anymore? You can change its settings by above command.

#### Remove role from project:

```
pgdist role-rm My_beautiful_role
```

**args - required**:

- `name` - name of role you want to remove from project

**NOTICE** - If you already made some role in your database, this will not help you to remove it from database, it only removes from project.

#### List roles in project:

```
pgdist role-list
```

Before PGdist installs project into the databse, it will check if roles defined in project exists in database. It checks roles and changes nologin/login option. If option password is set, PGdist will create file `username` in path defined in [distribution config file](#distribution-config-file-▲) with content `PGPASSWORD=GENERATED_PASSWORD`.



### File management [▲](#content)

#### Add file to project:

To add file to your project, move it to the `sql` directory if you are using your directory structure, or move it to the correct directory (`table.sql` to `tables`, `schema.sql` to `schema`, etc.) and run command below.

```
pgdist add /path/to/your/SQL/file_1 [/path/to/your/SQL/file_2]
```

**args - required**:

- `path` - *multiple* - path to file you want to add to your project

**args - optional**:

- `--all` - *enable* - adds all *NEW FILE* to your project

#### Remove file from project:

```
pgdist rm /path/to/your/SQL/file_1 [/path/to/your/SQL/file_2]
```

**args - required**:

- `path` - *multiple* - path to file you want to add to your project

**args - optional**:

- `--all` - *enable* - removes all *REMOVED FILE* from your project

This command will **ONLY** remove it from `pg_project.sql`, if you want to delete the file, you have to do it yourself.

#### Show status of project files:

```
pgdist status
```

- Shows files, which are in project directory.

- Files in project´s directory which have not been added to project: *NEW FILE*.

- Files in which are added to project but are not in project´s directory: *REMOVED FILE*.

#### Add part to project:

In case you need to divide your project to parts, use command below.

```
pgdist part-add [not_single]
```

**args - optional**:

- `transaction_type` - adds new part to `pg_project.sql` with *not single_transaction*, if not specified, *single_transaction* is taken instead

**NOTICE** - This still requires you to manage your parts, PGdist won´t remove or modify parts. If part order or something else does not fit you, you have to change it yourself.

#### Recommendations:

- Add your files to your project in the order as if you would be addding them to your database directly (this will ensure, that you won´t have to adjust import file order in `pg_project.sql`).  

**Example**: first you would add all your `schema.sql` into your project then everything else that depends on it.

- As the above point points out to file order, try to adjust or split your SQL dependencies in the order, so you don´t have to adjust your `version.sql` file.  

**NOTICE** - Table data from `sql/schema/data` will be added only in file created by `create-version`.



### Requires [▲](#content)

#### Add require to project:

If your project has dependency on some other project, you can add a require on other project.

```
pgdist require-add My_Other_Project https://url_or_ssh_to_your_other_project branch_name
```

**args - required**:

- `project` - name of required project

- `git` - git URL or SSH of required project

- `git_tree` - name of required project git branch


**NOTICE** - Above command works only when used before `create-version`.

#### Remove require from project:

Well if you changed your mind or your project just does not have dependency on other project, you can remove it:

```
pgdist require-rm My_Other_Project
```

**args - required**:

- `project` - name of project to remove from required projects



### DB parameters [▲](#content)

#### Set DB-parameters:

Before you load your project to database, you may want to set some things before crerating database.

```
pgdist dbparam-set OWNER My_beatufil_role ENCODING utf8 CONNECTION LIMIT -1
```

**args - required**:

- `dbparam` - parameters to create database with, see more: https://www.postgresql.org/docs/current/sql-createdatabase.html, PGdist will literally take it and put it at the end of command

#### Get DB-parameters:

Lists DB-parameters of your project.

```
pgdist dbparam-get
```



### Versions [▲](#content)

#### Test load:

Once you´re satisfied with your project, you can try to load it to database, to test, if it would even pass without errors.

```
pgdist test-load
```

**args - optional**:

- `--no-clean` - *enable* - after loading project to database, it won´t clean it

- `--pre-load` - path to file you want to load BEFORE loading project to database

- `--post-load` - path to file you want to load AFTER loading project to database

- `--pg_extractor` - *enable* - use PG extractor for PG dump, see more: https://github.com/omniti-labs/pg_extractor

- `--pg_extractor_basedir` - PG extractor dumps PG to this directory

It will try to load current state of your project to database.

**NOTICE** - This command requires develop configuration file to have setted *PGCONN* in section *pgdist*.

#### Create version:

If your `test-load` ended successfully, you may create version.  

```
pgdist create-version 1.0.0 [v1.0.0]
```

**args - required**:

- `version` - version of project

**args - optional**:

- `git_tag` - create version from git tag (if not specified, current file system version is taken instead)

- `-f` `--force` - *enable* - if version file already exists, rewrite it

The above command creates new file `My_Project--1.0.0.sql` in your `sql_dist` folder.  
In case your project is made from multiple parts `create-version` will make **new** `version file` for each part.

#### Version file

Version file contains header (which is almost identical to [project configuration file](#project-configuration-file)) and content from your source files.  
Header of simple version file might look like this:

```
--
-- pgdist project
-- name: My_Project
--
-- version: 1.0.0
--
-- part: 1
-- single_transaction
--
-- end header
--
```

**NOTICE** - Something can be added only when using this command, like `require-add` or *table data*

#### Create update:

You already made your first version and forgot to add something? Don´t worry, we got you.

```
pgdist create-update v1.0.0 1.0.1
```

**args - required**:

- `git_tag` - create update from git tag

- `new_version` - new version of project

**args - optional**:

- `-f` `--force` - *enable* - if update file already exists, rewrite it

- `--gitversion` - use this as old version name to create update from (only name/file purposes)

- `--no-clean` - *enable* - after loading project to database (parse purpose), it won´t clean it

- `--pre-load` - path to file you want to load, if `pre-load-old/new` is not specified, load **before both** projects

- `--pre-load-old` - path to file you want to load **before old** project

- `--pre-load-new` - path to file you want to load **before new** project

- `--post-load` - path to file you want to load, if `pre-load-old/new` is not specified, load **after both** projects

- `--post-load-old` - path to file you want to load **after old** project

- `--post-load-new` - path to file you want to load **after new** project

This command creates new file `My_Project--1.0.0--1.0.1.sql` in your `sql_dist` folder.  

**NOTICE** - `create-update` does not care about project parts, you need to define them yourself.

#### Update file

Once again, update file´s header is almost identical to both *version* and *project configuration* files.  
Header of simple update file:  

```
--
-- pgdist update
--
-- name: My_Project
--
-- old version: 1.0.0
-- new version: 1.0.1
--
-- role: My_beautiful_role password login
--
-- part: 1
-- not single_transaction
--
-- end header
--
```

As mentioned earlier, `create-update` does not care about project parts, so you have to do it yourself, but fear not, here´s how to do it.

1. Rename `My_Project-1.0.0--1.0.1.sql` to `My_Project-1.0.0--1.0.1--p1.sql` (`--p1` means part: 1, etc.).

2. Replace `-- part: 1` with number of part (`-- part: 2`, etc.).

3. For each part repeat step 1 and 2.

#### Test update:

Loads git tag version of your project to test database, then tries to use your update on it and in the end, it will print diff between old and new version.

```
pgdist test-update v1.0.0 1.0.1
```

**args - required**:

- `git_tag` - test update on git tag version

- `version` - version of project

**args - optional**:

- `--gitversion` - use this as old version name to test update from (only name/file purposes)

- `--no-clean` - *enable* - after loading project to database (parse purpose), it won´t clean it

- `--pre-load` - path to file you want to load, if `pre-load-old/new` is not specified, load **before both** projects

- `--pre-load-old` - path to file you want to load **before old** project

- `--pre-load-new` - path to file you want to load **before new** project

- `--post-load` - path to file you want to load, if `pre-load-old/new` is not specified, load **after both** projects

- `--post-load-old` - path to file you want to load **after old** project

- `--post-load-new` - path to file you want to load **after new** project

- `--pg_extractor` - *enable* - use PG extractor for PG dump, see more: https://github.com/omniti-labs/pg_extractor

- `--pg_extractor_basedir` - PG extractor dumps PG to this directory



### Project distribution [▲](#content)

**NOTICE** - Do not forget to correctly set up [distribution configuration file](#distribution-config-file-▲).

#### List projects:

To show list of installed and available projects and their updates:

```
pgdist list [My_Project [pg_database]]
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

If you want to show list of projects in some database without specifying project, use `-d` or `--dbname`.

#### Install project:

So once you have prepared version of your project, you can try to install it.

```
pgdist install My_Project pg_database [1.0.0]
```

**args - required**:

- `project` - name of project you want to install

- `dbname` - name of database to install to

**args - optional**:

- `version` - version of project to install, if not specified, latest is taken instead

- `--directory` - path to directory which contains install/update sql scripts

- `-C` `--create` - *enable* - if database does not exist, create it

- `-U` `--username` - PG username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PG host

- `-p` `--port` - port that PG listens to

Takes `My_Project--1.0.0.sql` and loads it to *pg_database*.  

#### Check updates:

After installation of your project, you may want to check for updates (you created obviously):

```
pgdist check-update [My_Project [pg_database [1.0.0]]]
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

#### Update project:

Now that you have checked for updates, you might want to update it with `My_Project--1.0.1.sql`.

```
pgdist update [My_Project [pg_database [1.0.1]]]
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

Takes `My_Project--1.0.0--1.0.1.sql` and loads it to *pg_database*.

If you don´t specify any parameter, PGdist will try to update each of your installed project.

#### Set version:

Set version in pgdist info of your installed project by force.

```
pgdist set-version My_Project pg_database 1.0.2
```

**args - required**:

- `project` - change info about project

- `dbname` - change info about project in database

- `version` - change info about project´s version

**args - optional**:

- `-U` `--username` - PG username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PG host

- `-p` `--port` - port that PG listens to

#### Get version:

```
pgdist get-version My_Project pg_database
```

**args - required**:

- `project` - get version of project

- `dbname` - get version of project in database

**args - optional**:

- `-U` `--username` - PG username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PG host

- `-p` `--port` - port that PG listens to

#### Clean info:

If you want to remove info (showed by `list`) about your project:

```
pgdist clean My_Project [pg_database]
```

**args - required**:

- `project` - clean info about project

**args - optional**:

- `dbname` - clean project from database

- `-U` `--username` - PG username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PG host

- `-p` `--port` - port that PG listens to



### Compare projects [▲](#content)

Let´s say you´ve installed some version of your project to your servers. Now you made a lot of changes in your project and you want to see the difference.  

#### Compare table data:

If you´ve added some table data to your project and you want to compare them with installed project table data, use command below to add them to comparison.

```
pgdist data-add some_table [table_column_1 [table_column_2]]
```

**args - required**:

- `table` - table you want to add to comparison

**args - optional**:

- `column` - *multiple* - columns you want to add to comparsion

#### Remove table data from comparison:

You don´t want to compare some table data anymore.

```
pgdist data-rm some_table
```

**args - required**:

- `table` - table you want to remove from comparison

#### List table data from comparison:

To see what table data you have added/removed:

```
pgdist data-list
```

#### Compare project:

Show difference between your current project and installed project:

```
pgdist diff-db root:password@my_server//pg_user:pg_password@/pg_database [v1.0.0]
```

**args - required**:

- `PGCONN` - connection to PG

**args - optional**:

- `git_tag` - compare project git tag with database (if not specified, current file system version is taken instead)

- `--diff-raw` - *enable* - compare raw SQL dumps

- `--no-clean` - *enable* - after loading project to database (parse purpose), it won´t clean it

- `--no-owner` - *enable* - don´t compare owners

- `--no-acl` - *enable* - don´t compare access privileges (grant/revoke commands)

- `--swap` - *enable* - swap data to compare

- `-w` `--ignore-all-space` - *enable* - ignore different whitespacing

- `--cache` - *enable* - cache remote dump for 4 hours

- `--pre-load` - path to file you want to load, load **before** current project

- `--post-load` - path to file you want to load, load **after** current project

- `--pre-remoted-load` - path to file you want to load, load **before** installed project

- `--post-remoted-load` - path to file you want to load, load **after** installed project

- `--pg_extractor` - *enable* - use PG extractor for PG dump, see more: https://github.com/omniti-labs/pg_extractor

- `--pg_extractor_basedir` - PG extractor dumps PG to this directory

Argument `--post-remoted-load` is very useful in case you create some hand-patch to unify versions.

#### Compare project and file:

Show difference between installed project and selected file:

```
pgdist diff-db-file root:password@my_server//pg_user:pg_password@/pg_database /path/to/your/SQL/file
```

Show difference between selected file and installed project:

```
pgdist diff-file-db /path/to/your/SQL/file root:password@my_server//pg_user:pg_password@/pg_database
```

**args - required**:

- `PGCONN` - connection to PG

- `file` - compare database with path to file

**args - optional**:

- `--diff-raw` - *enable* - compare raw SQL dumps

- `--no-clean` - *enable* - after loading project to database (parse purpose), it won´t clean it

- `--no-owner` - *enable* - don´t compare owners

- `--no-acl` - *enable* - don´t compare access privileges (grant/revoke commands)

- `--swap` - *enable* - swap data to compare

- `-w` `--ignore-all-space` - *enable* - ignore different whitespacing

- `--cache` - *enable* - cache remote dump for 4 hours

- `--pre-load` - path to file you want to load, load **before** current project

- `--post-load` - path to file you want to load, load **after** current project

- `--pre-remoted-load` - path to file you want to load, load **before** installed project

- `--post-remoted-load` - path to file you want to load, load **after** installed project

- `--pg_extractor` - *enable* - use PG extractor for PG dump, see more: https://github.com/omniti-labs/pg_extractor

- `--pg_extractor_basedir` - PG extractor dumps PG to this directory



## Authors

* Marian Krucina LinuxBox.cz

* Tadeáš Popov https://github.com/TadeasPopov

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE (Version 2) - see the COPYING file for details
