# 既存コードベース情報

## Product モデル

```ruby
class Product < ApplicationRecord
  scope :published, -> { where(published: true) }
  scope :draft, -> { where(published: false) }
  scope :in_stock, -> { where("stock > 0") }
  scope :out_of_stock, -> { where(stock: 0) }
  scope :price_between, ->(min, max) { where(price: min..max) }
  scope :price_under, ->(max) { where("price <= ?", max) }
  scope :newest_first, -> { order(created_at: :desc) }
  scope :oldest_first, -> { order(created_at: :asc) }
  scope :cheapest_first, -> { order(price: :asc) }
end
```

## スキーマ

```ruby
create_table "products", force: :cascade do |t|
  t.string "name", null: false
  t.decimal "price", precision: 10, scale: 2, null: false
  t.integer "stock", default: 0, null: false
  t.boolean "published", default: false, null: false
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
end
```
