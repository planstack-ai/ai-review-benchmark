## Notes

The benchmark service generates sample Ruby code to test AI code review capabilities. When generating sample code, it should follow Rails best practices including:
- Proper `dependent: :destroy` on associations to prevent orphaned records
- Correct use of `params` in controllers (not in model methods)
- Proper eager loading to avoid N+1 queries
