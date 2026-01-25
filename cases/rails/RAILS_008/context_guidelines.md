## Notes

When performing bulk updates on orders:
- Use `find_each { |order| order.update(...) }` to ensure callbacks are triggered
- Avoid `update_all` when callbacks contain important business logic (audit logging, notifications, inventory updates)
- If `update_all` is used intentionally for performance, ensure all skipped business logic is handled manually
