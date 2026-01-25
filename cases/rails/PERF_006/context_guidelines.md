## Usage Guidelines

- Never load entire tables into memory. Use `find_each` or `find_in_batches` for batch processing large datasets.

- Design cache keys carefully. Include all variables that affect the cached content (user_id, locale, etc.) to prevent showing wrong data.

