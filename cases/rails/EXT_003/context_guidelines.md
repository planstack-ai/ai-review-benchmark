## Usage Guidelines

- Never call external APIs inside database transactions. The transaction may rollback but the external call cannot be undone. Separate the transaction from external calls.

