# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  enum membership: { free: 0, standard: 1, premium: 2 }

  def premium?
    membership == "premium"
  end
end
```

## Order モデル

```ruby
class Order < ApplicationRecord
  belongs_to :user

  # rate: 支払い率（0.9 = 10%割引）
  def apply_discount(rate)
    self.total = subtotal * rate
  end
end
```
