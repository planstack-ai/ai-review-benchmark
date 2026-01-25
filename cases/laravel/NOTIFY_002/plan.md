# Low Stock Alert System

## Overview

Alert inventory managers when products reach low stock levels.

## Requirements

1. Monitor stock levels against thresholds
2. Send alerts when stock falls below threshold
3. Prevent duplicate alerts for same product
4. Clear alert status when restocked

## Alert Rules

- Alert when: current_stock < reorder_point
- Don't send duplicate alerts within 24 hours
- Send to all users with 'inventory_manager' role
