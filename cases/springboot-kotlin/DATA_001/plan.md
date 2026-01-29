# Order Items Entity Mapping

## Overview

Define the relationship between orders and order items. When an order is deleted, associated order items should be properly handled.

## Requirements

1. Order items must be associated with an order
2. Deleting an order should handle associated order items
3. No orphan order_item records should exist without a parent order
