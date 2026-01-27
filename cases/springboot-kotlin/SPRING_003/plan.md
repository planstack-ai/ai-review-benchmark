# Field Injection Testing for Order Processing Service

## Overview

This test case validates the proper implementation of field injection in a Spring Boot application for order processing functionality. The system requires dependency injection of an OrderService to handle business logic operations. The test should verify that the OrderService dependency is correctly injected and accessible for order processing operations.

## Requirements

1. Create a test class that demonstrates field injection of OrderService dependency
2. The OrderService dependency must be injected using Spring's dependency injection mechanism
3. The test class must be properly configured to work within Spring's test context
4. Include a test method that verifies the OrderService dependency is not null after injection
5. Include a test method that demonstrates the OrderService can be used to perform basic operations
6. The test class must use appropriate Spring Boot testing annotations
7. The OrderService dependency must be available for use in test methods without manual instantiation
8. The test should validate that the injected service maintains its expected behavior

## Constraints

1. The OrderService dependency must not be manually instantiated within the test class
2. The test must not use constructor injection or setter injection - only field injection
3. The test class must not contain any @Autowired annotations on constructors or setter methods
4. All test methods must pass when the dependency is properly injected
5. The test should fail gracefully if the dependency injection is not configured correctly

## References

See context.md for existing OrderService implementation and related Spring Boot configuration details.