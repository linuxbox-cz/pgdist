### Part add

For dividing project into parts. Adds new part to [project config. file](../../project_files/config.md).

```
pgdist part-add [transaction_type]

Example:
pgdist part-add not-single-transaction
```

**args - optional**:

- `transaction_type` - adds new part with *not single transaction*, if not specified, *single transaction* is taken instead



### Part rm

This command will remove specified part, and put all its files to previous part.  

**NOTICE** - PGdist still requires you to manage your parts, PGdist won´t remove or modify parts. If part order or something else does not fit you, you have to change it yourself.

```
pgdist part-rm <part_number>

Example:
$ pgdist part-rm 2
```

**args - required**:

- `part_number` - number of part you want to remove from your project

**args - optional**:

- `-f` `--force` - *enable* - if used, PGdist will also remove all files belonging to specified part
