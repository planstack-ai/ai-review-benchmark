# Order Tax Calculation with Exemptions

## Overview

The system calculates taxes for e-commerce orders, handling various tax exemption scenarios including tax-exempt customers, tax-free states (Oregon), and tax-exempt product categories (books, medical supplies, groceries). The system must also handle luxury tax for high-end items.

## Requirements

1. Calculate taxable subtotal excluding exempt items
2. Apply standard 8% tax rate to taxable items
3. Apply additional 2% luxury tax on jewelry, watches, and luxury electronics
4. Apply luxury tax to items over $1000 regardless of category
5. Exempt entire order if customer is tax-exempt
6. Exempt entire order if shipping to Oregon (no sales tax)
7. Exempt specific categories: books, medical_supplies, groceries
8. Calculate item-level discounts before determining taxable amount
9. Apply bulk discount (5%) for quantities of 10 or more
10. Use the current tax rate from system configuration (10%)

## Constraints

1. Tax rate must be retrieved from system configuration, not hardcoded
2. Tax exemptions are mutually exclusive (check customer first, then state, then categories)
3. Luxury tax applies in addition to standard tax
4. Item discounts reduce the taxable amount
5. Negative taxable amounts should be treated as zero

## References

See context.md for TaxRate configuration model and product category definitions.
