# Existing Codebase

## Payment Gateway Client

```java
@Component
public class PaymentGatewayClient {
    private final RestTemplate restTemplate;

    public PaymentGatewayClient(RestTemplateBuilder builder) {
        this.restTemplate = builder
            .setConnectTimeout(Duration.ofSeconds(10))
            .setReadTimeout(Duration.ofSeconds(30))
            .build();
    }

    public PaymentResponse chargeCard(String cardToken, BigDecimal amount) {
        // May throw HttpTimeoutException on timeout
        return restTemplate.postForObject(
            "https://api.paymentgateway.com/charge",
            new ChargeRequest(cardToken, amount),
            PaymentResponse.class
        );
    }
}
```

## Timeout Scenario

```
1. Customer submits order
2. Payment request sent to gateway
3. Network timeout after 30 seconds
4. Unknown if payment was processed!
5. Customer may have been charged
6. Order state is ambiguous
```

## Usage Guidelines

- Timeout does NOT mean payment failed - it's unknown
- Implement idempotency keys for retry safety
- Mark orders as PENDING_VERIFICATION on timeout
- Schedule job to verify payment status after timeout
- Never assume payment failed on timeout
