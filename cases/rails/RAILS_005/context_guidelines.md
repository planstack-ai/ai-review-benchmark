## Notes

When scheduling background jobs from within database transactions:
- Use `after_commit` callbacks instead of `after_save` to ensure jobs are only enqueued after the transaction successfully commits
- Jobs enqueued during a transaction may execute before the transaction commits, causing race conditions
- If a transaction rolls back, jobs scheduled with `after_save` will still execute with stale/invalid data
