#### Init

This command is used to initialize your project. It will create basic directory structure with project configuration file.  
Version and update scripts/files are in `sql_dist` folder.

```
pgdist init <project> [path]

Example:
$ pgdist init my_project /tmp/pgdist_project
Init project: my_project in pgdist_project
PGdist project inited in pgdist_project
```

**args - required**:

- `project` - name of your desired project

**args - optional**:

- `path` - path to folder to create project in
