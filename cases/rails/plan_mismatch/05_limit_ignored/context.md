# 既存コードベース情報

## CartItem モデル

```ruby
class CartItem < ApplicationRecord
  belongs_to :cart
  belongs_to :product

  MAX_QUANTITY = 100

  validates :quantity, numericality: { greater_than: 0, less_than_or_equal_to: MAX_QUANTITY }

  # 数量が上限を超えているか
  def quantity_exceeded?
    quantity > MAX_QUANTITY
  end

  # 数量を加算
  def add_quantity(amount)
    self.quantity += amount
  end
end
```

## Cart モデル

```ruby
class Cart < ApplicationRecord
  has_many :cart_items, dependent: :destroy
  belongs_to :user, optional: true

  def total_amount
    cart_items.sum { |item| item.product.price * item.quantity }
  end
end
```

## 例外クラス

```ruby
class CartQuantityExceededError < StandardError; end
```
