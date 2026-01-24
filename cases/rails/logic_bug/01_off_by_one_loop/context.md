# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  # ポイント残高を保持
  # points: integer, default: 0

  def add_points(amount)
    increment!(:points, amount)
  end

  def deduct_points(amount)
    raise InsufficientPointsError if points < amount
    decrement!(:points, amount)
  end
end
```

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "name", null: false
  t.string "email", null: false
  t.integer "points", default: 0, null: false
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
end
```
