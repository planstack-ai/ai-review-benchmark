# 既存コードベース情報

## Order モデル

```ruby
class Order < ApplicationRecord
  has_many :order_items
  has_many :products, through: :order_items

  scope :with_items, -> { includes(order_items: :product) }
end
```

## OrderItem モデル

```ruby
class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product
end
```
