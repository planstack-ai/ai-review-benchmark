# Order Management System with Item Loading

## Overview

This system manages customer orders and their associated items. The primary business requirement is to efficiently load orders along with their related items to display complete order information to users. The system should handle the relationship between orders and items while maintaining good performance characteristics.

## Requirements

1. Create an Order entity that represents customer orders with basic order information
2. Create an OrderItem entity that represents individual items within an order
3. Establish a proper relationship between Order and OrderItem entities
4. Implement a service method to retrieve orders with their associated items
5. Create a REST endpoint that exposes the order retrieval functionality
6. Ensure the system can handle multiple orders, each containing multiple items
7. The order loading functionality should return complete order information including all associated items
8. Implement proper error handling for cases where orders or items cannot be found
9. Use appropriate HTTP status codes and response formats for the REST API
10. Follow Spring Boot best practices for entity relationships and service layer design

## Constraints

1. Orders must have a valid identifier and basic order metadata
2. OrderItems must be properly associated with their parent order
3. The system should handle empty orders (orders with no items) gracefully
4. Database queries should be optimized to avoid performance issues
5. The REST API should return data in a structured JSON format
6. All entities should include proper validation annotations
7. The service layer should be transactional where appropriate

## References

See context.md for examples of existing Spring Boot implementations and entity relationship patterns.