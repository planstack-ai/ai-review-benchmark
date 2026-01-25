## Usage Guidelines

- Wrap related database operations in transactions to ensure atomicity. Use `requires_new: true` for nested transactions when inner operations should have independent commit/rollback behavior.

