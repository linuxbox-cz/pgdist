### Reuqire add

If your project has dependency on some other project, you can add a require on other project.

**NOTICE** - Below command works only when used before [`create-version`](create-version.md).

```
pgdist require-add <project> <git> <git_tree_ish>

Example:
$ pgdist require-add My_Other_Project https://url_or_ssh_to_your_other_project branch_name
```

**args - required**:

- `project` - name of required project

- `git` - git URL or SSH of required project

- `git_tree_ish` - indicates a tree, commit or tag object name of required project
