### Part update rm

This command will delete specified part.  

**NOTICE** - All data in specified part will be removed.

```
pgdist part-update-rm <old_version> <new_version> <part_number>

Example:
$ pgdist part-update-rm 1.0.0 1.0.1 2
```

**args - required**:

- `old_version` - old version of update script

- `new_version` - new version of update script

- `part_number` - number of part to remove
