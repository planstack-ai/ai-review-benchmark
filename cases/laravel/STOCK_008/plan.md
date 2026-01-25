# Low Stock Alert and Reorder

## Overview

Monitor stock levels and trigger reorder when below threshold.

## Requirements

1. Check stock levels against reorder point
2. Calculate reorder quantity based on lead time and demand
3. Create purchase orders automatically
4. Prevent duplicate reorders for pending purchase orders

## Business Rules

- Reorder when: available_stock <= reorder_point
- Reorder quantity = (daily_demand * lead_time_days) + safety_stock - current_stock
- Don't create new PO if existing PO is pending for same product
- One PO per product at a time
