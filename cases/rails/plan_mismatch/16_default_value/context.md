# 既存コードベース情報

## Product モデル

```ruby
class Product < ApplicationRecord
  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
  validates :stock, numericality: { greater_than_or_equal_to: 0 }

  scope :published, -> { where(published: true) }
  scope :in_stock, -> { where("stock > 0") }
end
```

## スキーマ

```ruby
create_table "products", force: :cascade do |t|
  t.string "name", null: false
  t.decimal "price", precision: 10, scale: 2, null: false
  t.integer "stock", default: 0, null: false     # デフォルト: 0
  t.boolean "published", default: false, null: false  # デフォルト: false
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
end
```
