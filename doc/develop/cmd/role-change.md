### Role change

You don´t like your role anymore? You can change it´s settings by above command.

```
pgdist role-change <name> [login | nologin] [password]

Example:
$ pgdist role-change My_beautiful_role nologin
```

**args - required**:

- `name` - name of role you want to change

**args - optional**:

- `login` - *choose* - *login* for enabling login for your role, otherwise *nologin*

- `password` - *choose* - *password* if you want PGdist to create and set password for your role when installing/updating your project
