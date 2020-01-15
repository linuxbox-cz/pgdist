#### Role rm

Removes role from your [`pg_project.sql`](../../project_files/config.md).

**NOTICE** - If you already made some role in your database, this will not help you to remove it from database, it only removes from project.

```
pgdist role-rm <name>

Example:
$ pgdist role-rm My_beautiful_role
```

**args - required**:

- `name` - name of role you want to remove from project
