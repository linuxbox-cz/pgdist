### Require rm

Well if you changed your mind or your project just does not have dependency on another project, you can remove it.

```
pgdist require-rm <project>

Example:
$ pgdist require-rm my_other_project
```

**args - required**:

- `project` - name of project to remove from required projects
