# 既存コードベース

## スキーマ

```ruby
# orders table
# - id: bigint
# - user_id: bigint (foreign key)
# - subtotal: decimal(10,2)
# - discount_amount: decimal(10,2)
# - tax_amount: decimal(10,2)
# - total: decimal(10,2)
# - status: integer (enum)
# - created_at: datetime
```

## モデル・サービス

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy

  TAX_RATE = 0.10  # 10%

  def apply_discount(rate)
    # rate: 支払い率（0.9 = 10%割引）
    self.total = subtotal * rate
  end

  def calculate_tax
    self.tax_amount = subtotal * TAX_RATE
  end
end
```
