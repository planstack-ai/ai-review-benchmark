# Product Catalog Service

## Overview

The product catalog service provides product information for the e-commerce platform. Products have multiple associations including categories, reviews, inventory records, and supplier information.

## Requirements

1. List products with basic information (name, price, SKU)
2. Show product detail page with full information
3. Most API calls only need basic product info

## Constraints

1. Product listing must be fast (< 100ms response time)
2. Most use cases only need product name and price
3. Reviews and supplier info are only shown on detail pages
