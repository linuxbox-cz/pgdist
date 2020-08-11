### Role list

Before PGdist installs project into the databse, it will check if roles defined in project exists in database. It checks roles and changes nologin/login option. If option password is set, PGdist will create file `username` in path defined in [distribution config file](../../distribution/config.md) with content `PGPASSWORD=GENERATED_PASSWORD`.

```
$ pgdist role-list
my_role nologin
```



### Role add

Below command creates role *my_beautiful_role* with ability to **login** and when installing, PGdist will create **password** and store it into directory defined in [distribution config file](../../distribution/config.md).  

```
pgdist role-add <name> [login | nologin] [password]

Example:
$ pgdist role-add my_beautiful_role login password
```

**args - required**:

- `name` - name of your role

**args - optional**:

- `login` - *choose* - *login* for enabling login for your role, otherwise *nologin*

- `password` - *choose* - *password* if you want PGdist to create and set password for your role when installing/updating your project



### Role change

You don´t like your role anymore? You can change it´s settings by above command.

```
pgdist role-change <name> [login | nologin] [password]

Example:
$ pgdist role-change my_beautiful_role nologin
```

**args - required**:

- `name` - name of role you want to change

**args - optional**:

- `login` - *choose* - *login* for enabling login for your role, otherwise *nologin*

- `password` - *choose* - *password* if you want PGdist to create and set password for your role when installing/updating your project



### Role rm

Removes role from your [`pg_project.sql`](../../project_files/config.md).

**NOTICE** - If you already made some role in your database, this will not help you to remove it from database, it only removes from project.

```
pgdist role-rm <name>

Example:
$ pgdist role-rm My_beautiful_role
```

**args - required**:

- `name` - name of role you want to remove from project
