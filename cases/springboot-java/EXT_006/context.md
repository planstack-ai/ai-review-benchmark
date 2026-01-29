# Existing Codebase

## Problem: Silent Failure

```java
// Bad: Error is swallowed, order appears shipped but no label exists
try {
    trackingNumber = shippingApi.generateLabel(order);
} catch (Exception e) {
    // Empty catch - error swallowed!
}
order.setStatus("SHIPPED");  // Marked as shipped even though label failed!
```

## Carrier API

```java
public interface ShippingCarrierClient {
    LabelResponse generateLabel(ShippingRequest request) throws CarrierException;
    void cancelLabel(String trackingNumber) throws CarrierException;
    TrackingInfo getTracking(String trackingNumber) throws CarrierException;
}
```

## Consequences of Swallowed Errors

1. Order marked as shipped but no tracking number
2. Customer receives wrong status
3. No notification to fix the issue
4. Package never ships, customer waits indefinitely
5. Operations unaware of problem until customer complains

## Usage Guidelines

- Never use empty catch blocks
- At minimum, log the error
- Set appropriate failure status
- Notify relevant team/system
- Consider retry with exponential backoff
- Distinguish recoverable vs non-recoverable errors
