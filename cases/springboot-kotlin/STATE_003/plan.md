# Stock Reservation System with Atomic Check-Then-Act Operations

## Overview

This system manages product inventory and handles stock reservations for an e-commerce platform. The core functionality involves checking available stock levels and atomically reserving items to prevent overselling. The system must handle concurrent reservation requests while maintaining data consistency and preventing race conditions that could lead to negative stock levels or double-booking of inventory.

## Requirements

1. The system shall provide a method to reserve a specified quantity of a product by product ID
2. The system shall verify that sufficient stock is available before making any reservation
3. The system shall atomically check stock availability and update inventory levels in a single operation
4. The system shall return a success indicator when a reservation is successfully completed
5. The system shall return a failure indicator when insufficient stock is available
6. The system shall prevent any scenario where stock levels become negative
7. The system shall handle concurrent reservation requests without data corruption
8. The system shall maintain accurate stock counts even under high concurrency
9. The system shall provide a method to query current stock levels for any product
10. The system shall initialize products with a specified starting stock quantity

## Constraints

1. Stock quantities must never fall below zero
2. Reservation quantities must be positive integers greater than zero
3. Product IDs must be valid and exist in the system before reservations can be made
4. The system must handle the case where multiple threads attempt to reserve the last available items simultaneously
5. All stock operations must be thread-safe and atomic
6. The system should gracefully handle attempts to reserve more items than are available

## References

See context.md for examples of existing implementations and common patterns used in similar stock management systems.