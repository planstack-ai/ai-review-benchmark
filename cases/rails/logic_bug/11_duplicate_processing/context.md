# 既存コードベース情報

## Order モデル

```ruby
class Order < ApplicationRecord
  belongs_to :user

  def points_granted?
    points_granted_at.present?
  end

  def mark_points_granted!
    update!(points_granted_at: Time.current)
  end

  def calculate_points
    (total_amount * 0.01).floor
  end
end
```

## User モデル

```ruby
class User < ApplicationRecord
  has_many :orders

  def add_points(amount)
    increment!(:points, amount)
  end
end
```

## スキーマ

```ruby
create_table "orders", force: :cascade do |t|
  t.bigint "user_id", null: false
  t.decimal "total_amount", precision: 10, scale: 2, null: false
  t.datetime "points_granted_at"
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
end

create_table "users", force: :cascade do |t|
  t.string "name", null: false
  t.integer "points", default: 0, null: false
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
end
```
