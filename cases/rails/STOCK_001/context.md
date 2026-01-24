# 既存コードベース

## スキーマ

```ruby
# products table
# - id: bigint
# - name: string
# - stock: integer
# - reserved_stock: integer
# - price: decimal(10,2)

# order_items table
# - id: bigint
# - order_id: bigint
# - product_id: bigint
# - quantity: integer
```

## モデル・サービス

```ruby
class Product < ApplicationRecord
  has_many :order_items

  scope :in_stock, -> { where('stock > reserved_stock') }

  def available_stock
    stock - reserved_stock
  end

  def reserve!(quantity)
    with_lock do
      raise InsufficientStock if available_stock < quantity
      increment!(:reserved_stock, quantity)
    end
  end
end
```
