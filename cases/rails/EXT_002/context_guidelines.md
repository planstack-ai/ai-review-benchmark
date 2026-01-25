## Usage Guidelines

- Webhook handlers must be idempotent - calling them multiple times with the same payload should have the same effect as calling once. Use idempotency keys or check for existing records.

