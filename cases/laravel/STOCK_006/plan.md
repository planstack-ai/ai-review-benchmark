# Preorder Stock Management

## Overview

Handle preorder purchases for products not yet in stock.

## Requirements

1. Accept preorders up to expected inventory quantity
2. Track preorder count against expected stock
3. Convert preorders to regular orders when stock arrives
4. Notify customers of stock arrival

## Business Rules

- Preorder limit = expected_quantity - current_preorder_count
- Regular stock and preorder stock are separate
- When stock arrives, fulfill preorders in FIFO order
