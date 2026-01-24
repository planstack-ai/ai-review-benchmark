# 既存コードベース

## スキーマ

```ruby
# payments table
# - id: bigint
# - order_id: bigint
# - external_id: string
# - amount: decimal(10,2)
# - status: string
# - idempotency_key: string

# webhook_logs table
# - id: bigint
# - event_id: string (unique)
# - processed_at: datetime
```

## モデル・サービス

```ruby
class PaymentGateway
  class TimeoutError < StandardError; end

  def self.charge(amount, idempotency_key:)
    # External payment API call
    response = HTTPClient.post('/charge', amount: amount, key: idempotency_key)
    response.success? or raise PaymentError
  end
end

class WebhookProcessor
  def self.process(event_id, &block)
    return if WebhookLog.exists?(event_id: event_id)
    yield
    WebhookLog.create!(event_id: event_id, processed_at: Time.current)
  end
end
```
