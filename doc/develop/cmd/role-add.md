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
