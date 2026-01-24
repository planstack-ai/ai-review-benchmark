# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  has_many :orders
  has_many :subscriptions

  enum membership: { free: 0, standard: 1, premium: 2 }

  def premium?
    membership == "premium"
  end

  def purchased_recently?(days)
    orders.where("created_at >= ?", days.days.ago).exists?
  end
end
```

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "name", null: false
  t.string "email", null: false
  t.integer "membership", default: 0, null: false
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
end

create_table "orders", force: :cascade do |t|
  t.bigint "user_id", null: false
  t.decimal "total_amount", precision: 10, scale: 2
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
end
```
