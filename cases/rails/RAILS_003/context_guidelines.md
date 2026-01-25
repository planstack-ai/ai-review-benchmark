## Usage Guidelines

- Be mindful of callback execution order. Callbacks in the same phase execute in the order they are defined. Ensure proper sequencing of operations.

- Be aware that `update_all` and `delete_all` skip callbacks and validations. Use them only when you intentionally want to bypass model logic.

