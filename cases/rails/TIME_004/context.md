# 既存コードベース

## スキーマ

```ruby
# campaigns table
# - id: bigint
# - name: string
# - starts_at: datetime
# - ends_at: datetime
# - timezone: string

# coupons table
# - id: bigint
# - code: string
# - expires_at: datetime
```

## モデル・サービス

```ruby
class Campaign < ApplicationRecord
  scope :active, -> {
    where('starts_at <= ? AND ends_at >= ?', Time.current, Time.current)
  }

  def active?
    starts_at <= Time.current && ends_at >= Time.current
  end
end

class Coupon < ApplicationRecord
  def expired?
    expires_at < Time.current
  end

  def valid_until?(date)
    expires_at >= date.end_of_day
  end
end
```
