## Usage Guidelines

- Use `count` for database COUNT queries. Avoid `length` or `size` on ActiveRecord relations as they load all records into memory.

- Never load entire tables into memory. Use `find_each` or `find_in_batches` for batch processing large datasets.

