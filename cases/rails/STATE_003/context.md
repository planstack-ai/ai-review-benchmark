# 既存コードベース

## スキーマ

```ruby
# orders table
# - id: bigint
# - status: integer (enum: pending, confirmed, shipped, delivered, canceled)
# - payment_status: integer (enum: unpaid, paid, refunded)
# - shipped_at: datetime
# - delivered_at: datetime
# - canceled_at: datetime
```

## モデル・サービス

```ruby
class Order < ApplicationRecord
  enum status: {
    pending: 0,
    confirmed: 1,
    shipped: 2,
    delivered: 3,
    canceled: 4
  }

  CANCELLABLE_STATUSES = %w[pending confirmed].freeze

  def can_cancel?
    CANCELLABLE_STATUSES.include?(status)
  end

  def cancel!
    raise CannotCancel unless can_cancel?
    update!(status: :canceled, canceled_at: Time.current)
  end
end
```
