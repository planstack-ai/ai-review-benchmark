# 既存コードベース情報

## Product モデル

```ruby
class Product < ApplicationRecord
  has_many :reservations

  validates :stock, numericality: { greater_than_or_equal_to: 0 }

  def reserve_stock!(quantity)
    with_lock do
      raise InsufficientStockError if stock < quantity
      decrement!(:stock, quantity)
    end
  end
end
```

## Reservation モデル

```ruby
class Reservation < ApplicationRecord
  belongs_to :product
  belongs_to :user

  validates :quantity, presence: true, numericality: { greater_than: 0 }
end
```

## スキーマ

```ruby
create_table "products", force: :cascade do |t|
  t.string "name", null: false
  t.integer "stock", default: 0, null: false
end

create_table "reservations", force: :cascade do |t|
  t.bigint "product_id", null: false
  t.bigint "user_id", null: false
  t.integer "quantity", null: false
end
```
