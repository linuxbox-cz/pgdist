#### Data add

If you´ve added some table data to your project and you want to compare them with installed project table data, use command below to add them to comparison.

```
pgdist data-add <table> [column...]

Example:
$ pgdist data-add some_table table_column_1 table_column_2
```

**args - required**:

- `table` - table you want to add to comparison

**args - optional**:

- `column` - *multiple* - columns you want to add to comparsion
