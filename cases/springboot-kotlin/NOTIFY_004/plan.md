# Shipping Notification Email with Customer Details

## Overview

The system needs to send shipping notification emails to customers when their orders are dispatched. These emails should include personalized customer information such as the customer's name, shipping address, and order details. The email template must handle cases where certain customer data fields may be optional or missing, ensuring that the email can still be sent successfully without causing runtime errors.

## Requirements

1. Send shipping notification emails when orders transition to SHIPPED status
2. Include customer name in the email greeting and content
3. Display complete shipping address information
4. Show order details including tracking number and carrier information
5. Handle optional customer data fields gracefully
6. Provide default values for missing or null customer information
7. Ensure null pointer exceptions do not occur during email generation
8. Use safe navigation operators for nullable fields
9. Format the email content professionally with proper fallback text
10. Log successful email sends with customer identifier

## Constraints

1. Customer name field may be null or empty in some legacy records
2. Email must be sent even if optional fields are missing
3. Template must not throw exceptions when accessing nullable properties
4. Default placeholder text should be professional (e.g., "Valued Customer")
5. All customer data access must use null-safe operations
6. Email service should validate required fields before attempting to send
7. Missing data should not prevent order status from updating to SHIPPED

## References

See context.md for existing database schema, entity definitions, and email template infrastructure.
