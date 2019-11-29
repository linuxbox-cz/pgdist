# PGdist - PostgreSQL projects control system

## Content

* [Description](#description)

	* [Develop config file](#develop-config-file)

		* [PGCONN](#pgconn)

	* [Distribution config file](#distribution-config-file)

* [Tutorial](#tutorial)

	* [Create project](#create-project)

	* [Manage SQL source files](#manage-sql-source-files)

	* [Create version (and test it)](#create-version)

	* [Create update (and test it)](#create-update)

	* [Install project (and diff it)](#install-project)

	* [Update project](#update-project)

	* [List log check](#list-log-check)

## Description
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

### Develop config file

Configuration file is located at `~/.pgdist`.

```
[pgdist]
test_db: pgdist@sqltest/postgres
```

- `test_db` - PG connection to testing postgres database.

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

Below PGCONN will define ssh connection to *my_server* with user *root* on port *8089*, then open postgres connection with PG user *postgres*, password *PASSWORD*, PG host *localhost*, listening port *5042*, database *test_database* and connection timeout *10 seconds*.  

```
root@my_server:8089//postgres:PASSWORD@localhost:5042/test_database?connection_timetout=10
```

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

- `pguser` - default PG user to connect with  

- `pgdatabase` - *optional* - name of database to connect to  

- `pghost` - *optional* - PG host  

- `pgport` - *optional* - port that PG listens to  



## Tutorial

**NOTICE** - This is only tutorial of some basic commands you will probably use, you will find more information in doc.md.

### Create project

First you want to do is make some directory where you want to initialize your project.

```
$ mkdir project_pg
```

Now that you have made your project folder lets enter it, and initialize pgdist project.

```
$ cd project_pg
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

After that, you can either create your directory structure under `sql` folder or use our recommended structure.

```
$ pgdist create-schema my_schema
Schema my_schema created.
```

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



### Manage SQL source files

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

As we can see, PGdist knows about them and also propose path to those files, now we can either add them one by one or use option `--all`.  

**IMPORTANT**  - Remember that you have to add files into project in the logical order (you can not create `schema.table` if `schema` does not exist). But do not worry
you can always adjust file order in `sql/pg_project.sql`.

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

In case you have deleted or you just want to remove file from project you can either directly remove it from `pg_project.sql` or use bellow command. Again you can write down all files you want to remove or use option `--all`.

**NOTICE** - `--all` just removes **deleted** files from `pg_project.sql`.

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

In case you need to divide your project to parts (parts with sinle/not signle transaction, cases like you create some table and after that you want to create index), we can add them to our `pg_project.sql`. For example we will create another file `indexes.sql`.

`indexes.sql` contains:

```
CREATE INDEX p_id ON my_schema.products USING btree(id);
```

Now because we know we will need two parts for this we will add another part. And add our file into project.

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

```
$ pgdist part-rm 2
```

This command will remove the second part and put all his files to previous part, but if you use `-f` `--force`, it will also remove all files from the specified part from `pg_project.sql`.



### Add roles

Because I added owner to table `products` and atuhorization to `my_schema`, I should also somehow define this role.

```
$ pgdist role-add my_role login password
```

After this command, PGdist will add below line into `pg_project.sql` and create password for specified role in `password_path`.

```
-- role: my_role password login
```

This will ensure that when trying to install this project, role which has been added to `pg_project.sql` will be created if they do not already exist.

But now I have decided that I do not want my role to login.

```
$ pgdist role-change my_role nologin
```

To remove role from `pg_project.sql` use command below.

```
$ pgdist role-rm my_role
```

To check if we specified our roles correctly, we will list them.

```
$ pgdist role-list
my_role nologin
```



### Create version

Now I am very satisfied with our project so why not create version from it? Because you have not tested it.

```
$ pgdist test-load
load project my_project to test pg
dump structure and data from test pg
checking element owners

Project my_project was loaded successfully.
```

This command will try to take our project and load it into test database. Now we can create version but first we will create a git-tag (it is not required but we will use it later).

```
$ git tag v1.0.0
$ pgdist create-version 1.0.0
Created file: my_project--1.0.0--p01.sql
Created file: my_project--1.0.0--p02.sql
```

If you use git-tag to create version, PGdist will take data from specified git-tag and from it it will try to create version, otherwise current state is taken instead. Notice that PGdist created two version files as part 1 and part 2, cool right? Yeah I know.

### Create update

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

After this command PGdist will create update file named `my_project--1.0.0-1.0.1.sql`. In it we will find some TODO we should do.

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

Like `create-version` might need parts, update might need parts too.

```
$ pgdist part-update-add 1.0.0 1.0.1 not-single-transaction
```

Notice that PGdist will only create update part with header so you have to put SQL into it yourself.

You also might want to remove update part.

```
$ pgdist part-update-rm 1.0.0 1.0.1 2
```

Last parameter is part number. It will delete update part file and data in it will be lost.



### Install project

So we are in phase where our project is beautiful and well-arranged and we want to install it.

```
$ pgdist install my_project project_pgdb 1.0.0 -C --directory ./sql_dist
CREATE DATABASE project_pgdb 
CREATE ROLE my_role NOLOGIN
Install my_project 1.0.0 part 1/2 to project_pgdb
Install my_project 1.0.0 part 2/2 to project_pgdb
Complete!
```

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



### Update project

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



### List log check

Well after time you will probably do many installations and updates so you can list installed projects and their updates and also a PGdist log.

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

Now we can see that we have installed my_project, in which database it is and also project version. It will also list available projects but you have to put install/update scripts into `install_path` or specify `--directory`. If you want to list only available updates for your projects use command below.

```
$ pgdist check-update my_project --directory ./sql_dist

Project updates:
============================================================================
 project             dbname              update
 my_project          project_pgdb        1.0.0 -> 1.0.1
============================================================================
```

From PGdist log you can see when was what created etc.

```
$ pgdist log
TIME                DBNAME                     PROJECT           VERSION COMMENT
2019-11-29 01:11:15 project_pgdb               my_project        v1.0.0  CREATE ROLE my_role nologin
2019-11-29 01:11:15 project_pgdb               my_project        v1.0.0  installed new version v1.0.0, part 1/2
2019-11-29 01:11:15 project_pgdb               my_project        v1.0.0  installed new version v1.0.0, part 2/2
```

###### You really did read it all? Lol.



## Authors

* Marian Krucina LinuxBox.cz

* Tadeáš Popov https://github.com/TadeasPopov



## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE (Version 2) - see the COPYING file for details
