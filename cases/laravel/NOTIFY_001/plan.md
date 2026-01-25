# Order Status Notification

## Overview

Send notifications when order status changes.

## Requirements

1. Notify customer on status changes
2. Different templates for different transitions
3. Include relevant order details
4. Respect notification preferences

## Notification Rules

- paid → processing: "Your order is being prepared"
- processing → shipped: "Your order has shipped" + tracking
- shipped → delivered: "Your order has been delivered"
- Only send if customer has email_notifications enabled
