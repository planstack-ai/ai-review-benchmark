# Bundle Stock Calculation System

## Overview

An e-commerce inventory management system needs to track product bundles that consist of multiple individual components. When customers view bundle products, they need to see accurate availability information based on the actual stock levels of all required components. The system must calculate bundle availability by determining how many complete bundles can be assembled from the current component inventory levels.

## Requirements

1. Bundle products must be defined with a list of required components and their quantities
2. Each component must specify the quantity needed per bundle unit
3. Bundle availability calculation must determine the maximum number of complete bundles possible
4. The calculation must use the minimum available quantity across all components when divided by their required quantities
5. Bundle stock level must update automatically when component stock levels change
6. Zero or negative component stock must result in zero bundle availability
7. Missing components must result in zero bundle availability
8. Bundle availability must be calculated in real-time when requested
9. The system must handle bundles with varying component quantity requirements (not just 1:1 ratios)
10. Bundle availability must be returned as a non-negative integer representing complete units

## Constraints

1. Component quantities in bundle definitions must be positive integers
2. Bundle calculations must not allow partial bundle availability (only complete units)
3. Component stock levels can be zero or negative, but bundle availability cannot be negative
4. Bundle definitions must contain at least one component
5. All components referenced in a bundle must exist in the inventory system
6. Bundle availability calculations must be performed using integer division to ensure whole units only

## References

See context.md for existing model structures and database relationships that should be leveraged for this implementation.