# 既存コードベース情報

## Product モデル

```ruby
class Product < ApplicationRecord
  validates :stock, numericality: { greater_than_or_equal_to: 0 }

  def reserve_stock(quantity)
    raise InsufficientStockError if stock < quantity
    update!(stock: stock - quantity)
  end
end

class InsufficientStockError < StandardError; end
```

## スキーマ

```ruby
create_table "products", force: :cascade do |t|
  t.string "name", null: false
  t.integer "stock", default: 0, null: false
  t.decimal "price", precision: 10, scale: 2, null: false
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
end
```
