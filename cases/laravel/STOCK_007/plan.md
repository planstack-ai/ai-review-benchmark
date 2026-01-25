# Multi-Warehouse Stock Transfer

## Overview

Transfer stock between warehouses for fulfillment optimization.

## Requirements

1. Verify source warehouse has sufficient stock
2. Create transfer record
3. Deduct from source, add to destination
4. Track in-transit inventory

## Business Rules

- Source warehouse must have available (non-reserved) stock
- Transfer creates "in transit" state until confirmed received
- Stock at source is deducted immediately
- Stock at destination is added only when transfer is confirmed
