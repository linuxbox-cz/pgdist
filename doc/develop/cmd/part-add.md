#### Part add

For dividing project into parts.

```
pgdist part-add [transaction_type]

Example:
pgdist part-add not-single-transaction
```

**args - optional**:

- `transaction_type` - adds new part to `pg_project.sql` with *not single transaction*, if not specified, *single transaction* is taken instead
