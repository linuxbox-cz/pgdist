### Part update add

If you want to add additional update parts, this command will create new [update](../../project_files/update.md) file.  

```
pgdist part-update-add <old_version> <new_version> [transaction_type]

Example:
$ pgdist part-update-add 1.0.0 1.0.1 not-single-transaction
```

**args - required**:

- `old_version` - old version of update script

- `new_version` - new version of update script

**args - optional**:

- `transaction_type` - new part created by PGdist will be with *not single transaction*, if not specified, *single transaction* is taken instead
