# Order Item with Product Reference

## Overview

Order items reference products purchased. Historical orders must display accurate information as it was at the time of purchase, even if product details change later.

## Requirements

1. Order items must show correct product information
2. Historical orders must display original product name and price
3. Product price changes should not affect past orders
4. Support product name changes without corrupting history
5. Order receipts must always be accurate

## Constraints

1. Past order data must remain immutable
2. Product updates should not retroactively change order display
3. Must maintain audit trail for financial records
4. Performance impact should be minimal

## References

See context.md for current implementation.
