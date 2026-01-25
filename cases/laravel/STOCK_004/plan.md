# Inventory Adjustment Service

## Overview

Handle manual inventory adjustments for damaged goods, audits, and corrections.

## Requirements

1. Record all inventory adjustments with reason
2. Update stock quantities
3. Maintain adjustment history for auditing
4. Prevent negative stock quantities

## Business Rules

- All adjustments must have a reason code
- Stock cannot go negative
- Adjustments require admin approval for quantities > 100
