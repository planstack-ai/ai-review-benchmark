# 既存コードベース情報

## Order モデル

```ruby
class Order < ApplicationRecord
  enum status: {
    pending: 0,
    paid: 1,      # 支払い完了
    shipped: 2,   # 発送済み
    delivered: 3  # 配達完了
  }

  VALID_TRANSITIONS = {
    pending: :paid,
    paid: :shipped,
    shipped: :delivered
  }.freeze

  def next_status
    VALID_TRANSITIONS[status.to_sym]
  end

  def can_transition_to?(new_status)
    next_status == new_status.to_sym
  end
end
```

## スキーマ

```ruby
create_table "orders", force: :cascade do |t|
  t.bigint "user_id", null: false
  t.integer "status", default: 0, null: false
  t.decimal "total_amount", precision: 10, scale: 2
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
end
```
