### Create schema

Creates default directory structure. If this directory structure does not fit your demands, you can use any other, this structure is only recommended.  
Source SQL files are located in `sql` folder.  

**NOTICE** - This will NOT create any *my_schema.sql* in my_schema folder.

```
pgdist create-schema <schema>

Example:
$ pgdist create-schema my_schema
Schema my_schema created.
```

**args - required**:

- `schema` - name of your desired schema
