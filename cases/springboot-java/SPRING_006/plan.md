# Spring Boot Circular Dependency Resolution Test Case

## Overview

This test case demonstrates proper handling of circular dependencies in a Spring Boot application within an e-commerce order processing system. The system involves an OrderService that needs to interact with a PaymentService, where both services may need to reference each other during order processing workflows. The implementation must resolve circular dependencies while maintaining proper service separation and functionality.

## Requirements

1. Create an OrderService class that depends on PaymentService for payment processing operations
2. Create a PaymentService class that may need to reference OrderService for order-related operations
3. Both services must be properly configured as Spring beans with appropriate annotations
4. The circular dependency between OrderService and PaymentService must be resolved using Spring's dependency injection mechanisms
5. OrderService must provide a method to create orders that utilizes PaymentService
6. PaymentService must provide a method to process payments that may need order information
7. The application must start successfully without circular dependency errors
8. Both services must be fully functional and able to perform their respective operations
9. The dependency resolution must not compromise the single responsibility principle of each service
10. All service methods must be accessible and properly wired through Spring's IoC container

## Constraints

1. Services must not use static methods or variables to break circular dependencies
2. The solution must use Spring Framework's built-in dependency injection features
3. Services must maintain proper encapsulation and not expose internal implementation details
4. The circular dependency resolution must not introduce memory leaks or performance issues
5. Both services must be testable in isolation when needed
6. The implementation must follow Spring Boot best practices for service layer design

## References

See context.md for additional implementation context and related patterns.