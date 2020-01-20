# Tutorial

**NOTICE** - This is only tutorial of some basic commands you will probably use, you will find more information in [documentation](doc.md).

## Content

* [Develop](#develop)
	* [How to create project](#how-to-create-project)
	* [How to manage SQL source files](#how-to-manage-SQL-source-files)
	* [How to manage roles](#how-to-manage-roles)
	* [How to create version](#how-to-create-version)
	* [How to create update](#how-to-create-update)
* [Distribution](#distribution)
	* [How to install project](#how-to-install-project)
	* [How to update project](#how-to-update-project)
	* [How to get project info](#how-to-get-project-info)

## Develop

### How to create project

First thing you want to do is make some directory where you want to initialize your project and enter it.

```
$ mkdir project_pg
$ cd project_pg
```

Now that you have made your project folder lets initialize pgdist project with [init command](develop/cmd/init.md).  
It will create this directory structure:

```
├── sql
│   └── pg_project.sql
└── sql_dist
```

After that, you can either create your directory structure under `sql` folder or use our recommended structure created by [create-schema command](develop/cmd/create-schema.md).
That creates following schema directory structure:

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

Now you have created your project and you are ready to add/remove files, etc..

### How to manage SQL source files

**Preparing SQL files**

Now that you have created your first project, let´s add some files to your project. For our example we will use `schema.sql` and `products.sql` files.

`schema.sql` contains:
```
CREATE SCHEMA my_schema AUTHORIZATION my_beautiful_role;
```

`products.sql` contains:
```
CREATE TABLE my_schema.products(
	id INT PRIMARY KEY,
	name TEXT
);

ALTER TABLE my_schema.products OWNER TO my_beautiful_role;
```

Put `schema.sql` into `sql/my_schema/schema` folder and `products.sql` into `sql/my_schema/tables` folder (only for better arrangement).  
In case you have your directory structure, just put it into `sql` folder.  
Now we want to add our files to our project, so let´s see if PGdist knows about those files with [status command](develop/cmd/status.md).

```
$ pgdist status
PROJECT: my_project
NEW FILE: sql/my_schema/schema/schema.sql
NEW FILE: sql/my_schema/tables/products.sql
```

As we can see, PGdist knows about them and also propose path to those files, now we can either add them one by one or all at once.  

**Add files**

We will add files to [project config. file](project_files/config.md) with [add command](develop/cmd/add.md).
Let´s see how does [project config. file](project_files/config.md) look now.

```
--
-- pgdist project-config
-- name: my_project
--
-- end header_data
--

-- part: 1
-- single_transaction

\ir my_schema/schema/schema.sql
\ir my_schema/tables/products.sql
```

**IMPORTANT** - Remember that you should add files into project in the logical order (you can not create `schema.table` if `schema` does not exist). But do not worry
you can always adjust file order in `sql/pg_project.sql`.

**Remove files**

In case you have deleted or you just want to remove file from project you can either directly remove it from [project config. file](project_files/config.md) or use [rm command](develop/cmd/rm.md).  
So now just for example I will delete those two added files and try PGdist status.

```
$ pgdist status
REMOVED FILE: sql/my_schema/schema/schema.sql
REMOVED FILE: sql/my_schema/tables/products.sql
```

Again, PGdist knows about it. So lets remove them with [rm command](develop/cmd/rm.md).  

**Add part**

In case you need to divide your project to parts (parts with sinle/not signle transaction, cases like you create some table and after that you want to create index), we can add them to our [project config. file](project_files/config.md).  
For example we will create another file `indexes.sql`.

`indexes.sql` contains:

```
CREATE INDEX p_id ON my_schema.products USING btree(id);
```

Now because we know we will need two parts for this we will add another part with [part-add command](develop/cmd/part-add.md) and add our file with [add command](develop/cmd/add.md) into project.  
If we look at our [project config. file](project_files/config.md) file we can see it has added another part and added our file into the second part.

```
--
-- pgdist project-config
-- name: my_project
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

It is not that smart, it just puts the file to the end of project-config, so if you want to add something to the first part, you have to adjust file order in [project config. file](project_files/config.md) then.

**Remove part**

Well you do not like your index anymore and you want to remove that useless second part? Use [part-rm command](develop/cmd/part-rm.md).  

### How to manage roles

**Add role**

Because I added owner to table `products` and authorization to `my_schema`, I should also somehow define this role with [role-add command](develop/cmd/role-add.md).  
After this command, PGdist will add below line into [project config. file](project_files/config.md).

```
-- role: my_beautiful_role password login
```

This will ensure that when trying to install this project, role which has been added to [project config. file](project_files/config.md) will be created if they do not already exist.

**Change role**

But now I have decided that I do not want my role to login so i will use [role-change command](develop/cmd/role-change.md).  
Again [project config. file](project_files/config.md) will be adjusted.

```
-- role: my_beautiful_role password nologin
```

**Remove role**

To remove role from [project config. file](project_files/config.md) use command [role-rm command](develop/cmd/role-rm.md).

**List roles**

To check if we specified our roles correctly, we can list them with [role-list command](develop/cmd/role-list.md).



### How to create version

**Test load**

Now I am very satisfied with our project so why not create version from it? Because you have not tested it with [test-load command](develop/cmd/test-load.md).

**Create version**

Now we can create version but first we will create a git-tag (it is not required but we will use it later).

```
$ git tag v1.0.0
```

Now use [create-version command](develop/cmd/create-version.md).
If you use git-tag to create version, PGdist will take data from specified git-tag and from it it will try to create version, otherwise current state is taken instead. Notice that PGdist created two version files as part 1 and part 2, cool right? Yeah I know.



### How to create update

**Preparing SQL files**

Well let´s change our SQL a little bit. Add new file `customers.sql` and put it into `sql/my_schema/tables` and add it to our project with [add command](develop/cmd/add.md).

`customers.sql` contains:

```
CREATE TABLE my_schema.customers(
	id INT PRIMARY KEY,
	first_name TEXT,
	last_name TEXT
);

ALTER TABLE my_schema.customers OWNER TO my_beautiful_role;
```

Change `products.sql` a little bit.

`products.sql` contains:

```
CREATE TABLE my_schema.products(
	id INT PRIMARY KEY,
	name TEXT,
	price INT
);

ALTER TABLE my_schema.products OWNER TO my_beautiful_role;
```

**Create update**

Now that we have made some changes, we want to create update with [create-update command](develop/cmd/create-update.md).
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
Use [test-update command](develop/cmd/test-update.md).  
It will try to load and compare current state of project with updated state which means if you do not see any green/red lines then you did everything right.

**Add update part**

Like [create-version command](develop/cmd/create-version.md) might need parts, update might need parts too. Let´s add part with [part-update-add command](develop/cmd/part-update-add.md).  
Notice that PGdist will only create update part with header so you have to put your SQL into it by yourself.

**Remove update part**

You also might want to remove update part with [part-update-rm command](develop/cmd/part-update-rm.md).



## Distribution

### How to install project

So we are in phase where our project is beautiful and well-arranged and we want to install it with [install command](distribution/cmd/install.md).

**Diff between project and database**

Yaaay! We got it, we installed version v1.0.0. Now we can show diff. between our current project (version 1.0.1) and database (version 1.0.0) with [diff-db command](develop/cmd/diff-db.md).  
Now we can see that in our current project state we added new table and changed the old one which is absolutely correct.

### How to update project

Now we are ready to update our project in database with [update command](distribution/cmd/update.md).

### How to get project info

**List installed/available projects**

Well after time you will probably do many installations and updates so you can list installed projects and their updates with [list command](distribution/cmd/list.md).
Below is list after update.

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

From PGdist log you can see when was what created etc.. So use [log command](distribution/cmd/log.md).
