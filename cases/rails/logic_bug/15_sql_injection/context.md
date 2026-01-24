# 既存コードベース情報

## Product モデル

```ruby
class Product < ApplicationRecord
  scope :search_by_name, ->(keyword) {
    where("name LIKE ?", "%#{sanitize_sql_like(keyword)}%")
  }

  scope :published, -> { where(published: true) }
end
```

## スキーマ

```ruby
create_table "products", force: :cascade do |t|
  t.string "name", null: false
  t.text "description"
  t.decimal "price", precision: 10, scale: 2
  t.boolean "published", default: false
  t.datetime "created_at", null: false
end
```
