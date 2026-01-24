# 既存コードベース

## スキーマ

```ruby
# orders table
# - id: bigint
# - user_id: bigint
# - status: integer (enum)
# - total: decimal(10,2)
```

## モデル・サービス

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy

  enum status: { pending: 0, confirmed: 1, shipped: 2, delivered: 3 }

  validates :total, numericality: { greater_than_or_equal_to: 0 }

  scope :active, -> { where.not(status: :canceled) }
end
```
