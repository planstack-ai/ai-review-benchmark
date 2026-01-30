# Existing Codebase

## Problem Scenario

```
Import 100 products from CSV
50 already exist (duplicate SKU)
Report says: "100 products imported"  -- Wrong!
Should say: "50 new, 50 skipped (duplicate)"
```

## Usage Guidelines

- Track insert vs update counts separately
- Use repository methods that return affected row counts
