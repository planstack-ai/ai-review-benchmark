# Order Service with Premium Member Discount

## Overview

The system needs to provide an order service for an e-commerce platform that offers tiered membership benefits. Premium and VIP members should receive discounts on their purchases, while STANDARD members pay full price. The service handles order creation, order history retrieval, and price calculation.

## Requirements

1. Create an order service that manages order creation and retrieval
2. Apply member discount only to PREMIUM and VIP membership types
3. STANDARD membership type customers pay full price without discount
4. Look up customers by email address
5. Calculate discount using the existing PricingService
6. Store orders with subtotal, discount amount, and total amount
7. Provide order history retrieval for customers sorted by creation date (descending)
8. Use constructor injection for dependencies

## Constraints

1. Customer must exist in the system (throw exception if not found by email)
2. Discount eligibility is determined solely by MembershipType enum (PREMIUM or VIP)
3. Use existing repository methods for data access
4. Use existing PricingService for discount and total calculations
5. All monetary calculations should use BigDecimal

## References

See context.md for existing entity definitions, repository interfaces, and service contracts.
