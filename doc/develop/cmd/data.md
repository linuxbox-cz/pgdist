### Data list

To see what table data you have added/removed:

```
pgdist data-list
```



### Data add

If you´ve added some table data to your project and you want to compare them with installed project table data, use command below to add them to comparison.

```
pgdist data-add <table> [column... | --exclude column...]

Example:

$ pgdist data-add some_table table_column_1 table_column_2

Example for arg --exclude:

$ pgdist data-add some_table --exclude table_column_1 table_column_2
```

**args - required**:

- `table` - table you want to add to comparison

**args - optional**:

- `--exclude column...` - columns you want to remove from comparison (at least one column must be included)

- `column` - *multiple* - columns you want to add to comparsion



### Data rm

You don´t want to compare some table data anymore.

```
pgdist data-rm <table>

Example:
pgdist data-rm some_table
```

**args - required**:

- `table` - table you want to remove from comparison
