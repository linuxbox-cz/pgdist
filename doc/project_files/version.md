### Project version file

Version file contains header (which is almost identical to [project config file](config.md)) and content from your source files.  
Header of simple version file might look like this:

```
--
-- pgdist project
-- name: My_Project
--
-- version: 1.0.0
--
-- part: 1
-- single_transaction
--
-- end header
--
```

**NOTICE** - Each part has its own header defining which transaction to use, parts in [project config file](config.md) are only used with [create-version](../develop/cmd/create-version.md) command.
