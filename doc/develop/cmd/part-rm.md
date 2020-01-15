#### Part rm

This command will remove specified part, and put all its files to previous part.  

**NOTICE** - PGdist still requires you to manage your parts, PGdist won´t remove or modify parts. If part order or something else does not fit you, you have to change it yourself.

```
pgdist part-rm <part_number>

Example:
pgdist part-rm 2
```

**args - required**:

- `part_number` - number of part you want to remove from your project

**args - optional**:

- `-f` `--force` - *enable* - if used, PGdist will also remove all files belongig to specified part
