### Project update file

Once again, update file´s header is almost identical to both [project version file](version.md) and [project config file](config.md) files.  
Header of simple update file:  

```
--
-- pgdist update
--
-- name: my_project
--
-- old version: 1.0.0
-- new version: 1.0.1
--
-- role: My_beautiful_role password login
--
-- part: 1
-- not single_transaction
--
-- end header
--
```

As you will find out, [create-update](../develop/cmd/create-update.md) does not care about project parts, so you have to do it yourself, but fear not, here´s how to do it.

1. Rename `my_project-1.0.0--1.0.1.sql` to `my_project-1.0.0--1.0.1--p1.sql` (`--p1` means part: 1, etc.).

2. Replace `-- part: 1` with number of part (`-- part: 2`, etc.).

3. For each part repeat step 1 and 2.

[**BACK TO DOCS**](../doc.md)  
[**BACK TO TUTORIAL**](../tutorial.md)  
