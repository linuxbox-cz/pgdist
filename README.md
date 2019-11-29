# PGdist - PostgreSQL projects control system

## Content

* [Description](#description)

* [Configuration](#configuration)

	* [Develop config](#develop-config-file)

		* [PGCONN](#pgconn)

	* [Project config](#project-config-file)

	* [Project version](#project-version-file)

	* [Project update](#project-update-file)

	* [Distribution config](#Distribution-config-file)

* [Tutorial](#tutorial)

	* [Develop](#develop)

		* [How to create project](#how-to-create-project)

		* [Manage SQL source files](#manage-sql-source-files)

		* [How to create version](#how-to-create-version)

		* [How to create update](#how-to-create-update)

	* [Distribution](#distribution)

		* [How to install project](#how-to-install-project)

		* [How to update project](#how-to-update-project)

		* [How to get project info](#how-to-get-project-info)

## Description
Let me introduce our project PGdist, used for PostgreSQL projects management from development to production.
URL: https://github.com/linuxbox-cz/pgdist

PGdist can:
- manage source files, collaborating with Git
- test project installation in PostgreSQL
- help to create update scripts and test it for mistakes
- display project‘s diff and existing database structure
- watch for proper role creation in database
- allow dependency settings
- compare data in tables
- make installations and updates on production server (inc. roles, dependencies)
- allow to split install and update scripts to parts, intended to be or not to be done in particular transaction
- show diffs in structured and colored mode

PGdist requires:
- PostgreSQL
- Git

The main motivation was standardization of many projects in PostgreSQL.  
PGdist will help us to create new version and its rpm package.  
On the other hand, it will install or update the project from rpm on production server.  
PGdist also can compare very old installation (and possible hand-made changes) and help us to prepare update script to standard version.  
PGdist also requires a little bit of **DIY - do it yourself**.  

**Develop part** - It is for usage on local computer. It cooperates with git.  

**Distribution part** - It is for usage on production server.



## Configuration

### Develop config file

Configuration file is located at `~/.pgdist`. It is used when test loading projects to database.

```
[pgdist]
test_db: pgdist@sqltest/postgres
```

- `test_db` - PostgreSQL connection to testing postgres database.



#### PGCONN

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

Below PGCONN will define ssh connection to *my_server* with user *root* on port *8089*, then open postgres connection with PostgreSQL user *postgres*, password *PASSWORD*, PostgreSQL host *localhost*, listening port *5042*, database *test_database* and connection timeout *10 seconds*.  

```
root@my_server:8089//postgres:PASSWORD@localhost:5042/test_database?connection_timetout=10
```



### Project config file

File `sql/pg_project.sql` is project configuration file. It contains header with some info and settings (project name, roles, table_data, parts, etc.) for command [create-version](#create-version) and [create-update](#create-update). It also contains paths to source files.  

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



### Project version file

Version file contains header (which is almost identical to [project config file](#project-config-file)) and content from your source files.  
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

**NOTICE** - Each part has its own header defining which transaction to use, parts in [pg_project.sql](#project-config-file) are only used with [create-version](#create-version) command.



### Project update file

Once again, update file´s header is almost identical to both [project version](#project-version-file) and [project config file](#project-config-file) files.  
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

As you will find out, [create-update](#create-update) does not care about project parts, so you have to do it yourself, but fear not, here´s how to do it.

1. Rename `My_Project-1.0.0--1.0.1.sql` to `My_Project-1.0.0--1.0.1--p1.sql` (`--p1` means part: 1, etc.).

2. Replace `-- part: 1` with number of part (`-- part: 2`, etc.).

3. For each part repeat step 1 and 2.



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

- `password_path` - path to roles passwords  

- `pguser` - default PostgreSQL user to connect with  

- `pgdatabase` - *optional* - name of database to connect to  

- `pghost` - *optional* - PostgreSQL host  

- `pgport` - *optional* - port that PostgreSQL listens to  



## Tutorial

**NOTICE** - This is only tutorial of some basic commands you will probably use, you will find more information in doc.md.



### Develop

#### How to create project

First thing you want to do is make some directory where you want to initialize your project and enter it.

```
$ mkdir project_pg
$ cd project_pg
```

Now that you have made your project folder lets initialize pgdist project.

```
$ pgdist init MyProject
Init project: MyProject in project_pg
PGdist project inited in project_pg
```

Above command should create directory structure as follows:

```
├── sql
│   └── pg_project.sql
└── sql_dist
```

After that, you can either create your directory structure under `sql` folder or use our recommended structure (which will create below command).

```
$ pgdist create-schema my_schema
Schema my_schema created.
```

That creates followin schema directory structure.

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



#### Manage SQL source files

**Preparing SQL files**

Now that you have created your first project, let´s add some files to your project. For our example we will use `schema.sql` and `products.sql` files.

`schema.sql` contains:
```
CREATE SCHEMA my_schema AUTHORIZATION my_role;
```

`products.sql` contains:
```
CREATE TABLE my_schema.products(
	id INT PRIMARY KEY,
	name TEXT
);

ALTER TABLE my_schema.products OWNER TO my_role;
```

Put `schema.sql` into `sql/my_schema/schema` folder and `products.sql` into `sql/my_schema/tables` folder (only for better arrangement). In case you have your
directory structure, just put it into `sql` folder. Now we want to add our files to our project, so let´s see if PGdist knows about those files.

```
$ pgdist status
PROJECT: MyProject
NEW FILE: sql/my_schema/schema/schema.sql
NEW FILE: sql/my_schema/tables/products.sql
```

As we can see, PGdist knows about them and also propose path to those files, now we can either add them one by one or all at once.  

**Add files**

One by one:
```
$ pgdist add sql/my_schema/schema/schema.sql sql/my_schema/tables/products.sql
Added to project:
	my_schema/schema/schema.sql
Added to project:
	my_schema/tables/products.sql

If you need, change order of files in project file sql/pg_project.sql
```

Using option `--all`:
```
$ pgdist add --all
Added to project:
	my_schema/schema/schema.sql
Added to project:
	my_schema/tables/products.sql

If you need, change order of files in project file sql/pg_project.sql
```

Let´s see how does `pg_project.sql` look now.

```
--
-- pgdist project-config
-- name: MyProject
--
-- end header_data
--

-- part: 1
-- single_transaction

\ir my_schema/schema/schema.sql
\ir my_schema/tables/products.sql
```

We can see that project-config containts some header with project name, part, transaction type and finally our files. Here you can manage
the order of files.  

**IMPORTANT**  - Remember that you have to add files into project in the logical order (you can not create `schema.table` if `schema` does not exist). But do not worry
you can always adjust file order in `sql/pg_project.sql`.

**Remove files**

In case you have deleted or you just want to remove file from project you can either directly remove it from `pg_project.sql` or use bellow command. Again you can write down all files you want to remove or all at once.

So now just for example I will delete those two added files and try PGdist status.

```
$ pgdist status
REMOVED FILE: sql/my_schema/schema/schema.sql
REMOVED FILE: sql/my_schema/tables/products.sql
```

Again, PGdist knows about it. So lets remove them.

```
$ pgdist rm --all
Removed from project:
	my_schema/schema/schema.sql
Removed from project:
	my_schema/tables/products.sql
```

**NOTICE** - `--all` just removes **deleted** files from `pg_project.sql`.

In case you need to divide your project to parts (parts with sinle/not signle transaction, cases like you create some table and after that you want to create index), we can add them to our `pg_project.sql`. For example we will create another file `indexes.sql`.

`indexes.sql` contains:

```
CREATE INDEX p_id ON my_schema.products USING btree(id);
```

Now because we know we will need two parts for this we will add another part. And add our file into project.

**Add part**

```
$ pgdist part-add not-single-transaction
$ pgdist add --all
Added to project:
	my_schema/indexes/indexes.sql

If you need, change order of files in project file sql/pg_project.sql
```

If we look at our `pg_project.sql` file we can see it has added another part a added our file into the second part.

```
--
-- pgdist project-config
-- name: MyProject
--
-- end header_data
--

-- part: 1
-- single_transaction

\ir my_schema/schema/schema.sql
\ir my_schema/tables/products.sql

-- part: 2
-- not single_transaction

\ir my_schema/indexes/indexes.sql
```

It is not that smart, it just puts the file to the end of project-config, so if you want to add something to the first part, you have to adjust file order in `pg_project.sql` then.

Well you do not like your index anymore and you want to remove that useless second part? Use this.

**Remove part**

```
$ pgdist part-rm 2
```

This command will remove specified part (by number) and put all his files to previous part, but if you use `-f` `--force`, it will also remove all files from the specified part from `pg_project.sql`.



**Add role**

Because I added owner to table `products` and authorization to `my_schema`, I should also somehow define this role.

```
$ pgdist role-add my_role login password
```

After this command, PGdist will add below line into `pg_project.sql` and create password for specified role in `password_path`.

```
-- role: my_role password login
```

This will ensure that when trying to install this project, role which has been added to `pg_project.sql` will be created if they do not already exist.

**Change role**

But now I have decided that I do not want my role to login.

```
$ pgdist role-change my_role nologin
```

**Remove role**

To remove role from `pg_project.sql` use command below.

```
$ pgdist role-rm my_role
```

To check if we specified our roles correctly, we will list them.

```
$ pgdist role-list
my_role nologin
```



#### How to create version

**Test load**

Now I am very satisfied with our project so why not create version from it? Because you have not tested it.

```
$ pgdist test-load
load project my_project to test pg
dump structure and data from test pg
checking element owners

Project my_project was loaded successfully.
```

This command will try to take our project and load it into test database

**Create version**

Now we can create version but first we will create a git-tag (it is not required but we will use it later).

```
$ git tag v1.0.0
$ pgdist create-version 1.0.0
Created file: my_project--1.0.0--p01.sql
Created file: my_project--1.0.0--p02.sql
```

If you use git-tag to create version, PGdist will take data from specified git-tag and from it it will try to create version, otherwise current state is taken instead. Notice that PGdist created two version files as part 1 and part 2, cool right? Yeah I know.



#### How to create update

**Preparing SQL files**

Well let´s change our SQL a little bit. Add new file `customers.sql` and put it into `sql/my_schema/tables` and add it to our project.

`customers.sql` contains:

```
CREATE TABLE my_schema.customers(
	id INT PRIMARY KEY,
	first_name TEXT,
	last_name TEXT
);

ALTER TABLE my_schema.customers OWNER TO my_role;
```

Add it to project.

```
$ pgdist add --all
Added to project:
	my_schema/tables/customers.sql

If you need, change order of files in project file sql/pg_project.sql
```

And change `products.sql` a little bit.

`products.sql` contains:

```
CREATE TABLE my_schema.products(
	id INT PRIMARY KEY,
	name TEXT,
	price INT
);

ALTER TABLE my_schema.products OWNER TO my_role;
```

**Create update**

Now that we have made some changes, we want to create update.

```
$ pgdist create-update v1.0.0 1.0.1
load project my_project to test pg
dump structure and data from test pg
load project my_project to test pg
dump structure and data from test pg
Edit created file: sql_dist/my_project--1.0.0--1.0.1.sql
and test it by 'pgdist test-update v1.0.0 1.0.1'
```

First parameter is git-tag (that is why we have created it earlier) and second is new version.

After this command PGdist will create update file named `my_project--1.0.0--1.0.1.sql`. In it we will find some TODO we should do.

```
--
-- table: my_schema.products
--

-- TODO: ALTER TABLE my_schema.products

-- +price integer

-- end table: my_schema.products
```

Well our new table was added succesfuly but PGdist does not know what to do with table when it is altered so it is your job to do it. We will adjust these lines as follows.

```
--
-- table: my_schema.products
--

ALTER TABLE my_schema.products ADD price INT;

-- end table: my_schema.products
```

**Test update**

Now that we have our update let´s put it straight into production right? No.


```
$ pgdist test-update v1.0.0 1.0.1
load project my_project to test pg
load update my_project 1.0.0 > 1.0.1 to test pg
dump structure and data from test pg
load project my_project to test pg
dump structure and data from test pg
checking element owners
```

It will try to load and compare current state of project with updated state which means if you do not see any green/red lines then you did everything right.

**Add update part**

Like `create-version` might need parts, update might need parts too.

```
$ pgdist part-update-add 1.0.0 1.0.1 not-single-transaction
```

Notice that PGdist will only create update part with header so you have to put SQL into it yourself.

**Remove update part**

You also might want to remove update part.

```
$ pgdist part-update-rm 1.0.0 1.0.1 2
```

Last parameter is part number. It will delete update part file and data in it will be lost.



### Distribution

For most of distribution commands you can use options below:

- `-U` `--username` - PostgreSQL username to connect with

- `-d` `--dbname` - name of database to connect to

- `-H` `--host` - PostgreSQL host

- `-p` `--port` - port that PostgreSQL listens to

I will not show their usage in this tutorial, but they are described in doc.md.



#### How to install project

So we are in phase where our project is beautiful and well-arranged and we want to install it.

```
$ pgdist install my_project project_pgdb 1.0.0 -C --directory ./sql_dist
CREATE DATABASE project_pgdb 
CREATE ROLE my_role NOLOGIN
Install my_project 1.0.0 part 1/2 to project_pgdb
Install my_project 1.0.0 part 2/2 to project_pgdb
Complete!
```

**Diff between project and database**

Yaaay! We got it, we installed version v1.0.0. Now we can show diff between our current project (version 1.0.1) and database.

```
$ pgdist diff-db postgres@/project_pgdb
dump remote
load dump to test pg
dump structure and data from test pg
load project my_project to test pg
dump structure and data from test pg
New tables:
		my_schema.customers

Table my_schema.products is different:
		+price integer
```

Now we can see that in our current project state we added new table and changed the old one which is absolutely correct.



#### How to update project

You will need to specify which project, to which database and what version, if version is not specified, latest is taken instead.

```
$ pgdist update my_project project_pgdb 1.0.1 --directory ./sql_dist

Project updates:
============================================================================
 project             dbname              update
 my_project          project_pgdb        1.0.0 -> 1.0.1
============================================================================

Update my_project in project_pgdb 1.0.0 > 1.0.1
Complete!
```



#### How to get project info

**List installed/available projects**

Well after time you will probably do many installations and updates so you can list installed projects and their updates.

```
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

Above is list before update, below after update.

```
Installed projects:
============================================================================
 project             dbname              version   from      part parts
 my_project          project_pgdb        1.0.1     1.0.0     1    1   
============================================================================
```

Now we can see that we have installed my_project, in which database it is and also project version. It will also list available projects but you have to put install/update scripts into `installation_path` or specify `--directory`.

**Check for updates**

If you want to list only available updates for your projects use command below.

```
$ pgdist check-update my_project --directory ./sql_dist

Project updates:
============================================================================
 project             dbname              update
 my_project          project_pgdb        1.0.0 -> 1.0.1
============================================================================
```

**Show PGdist log**

From PGdist log you can see when was what created etc.

```
$ pgdist log
TIME                DBNAME                     PROJECT           VERSION COMMENT
2019-11-29 01:11:15 project_pgdb               my_project        1.0.0   CREATE ROLE my_role nologin
2019-11-29 01:11:15 project_pgdb               my_project        1.0.0   installed new version 1.0.0, part 1/2
2019-11-29 01:11:15 project_pgdb               my_project        1.0.0   installed new version 1.0.0, part 2/2
2019-11-29 02:11:31 project_pgdb               my_project        1.0.1   updated from version 1.0.1 to 1.0.0, part 1/1
```



## Authors

* Marian Krucina LinuxBox.cz

* Tadeáš Popov https://github.com/TadeasPopov



## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE (Version 2) - see the COPYING file for details
