# 既存コードベース情報

## Order モデル

```ruby
class Order < ApplicationRecord
  # ステータス値（レガシーシステムからの移行により大文字で保存されている場合がある）
  # "pending", "PENDING", "Pending" などが混在
  CANCELLABLE_STATUSES = %w[pending confirmed].freeze
  NON_CANCELLABLE_STATUSES = %w[shipped delivered].freeze

  belongs_to :user
  has_many :order_items

  def cancellable_status?
    CANCELLABLE_STATUSES.include?(status&.downcase)
  end
end
```

## スキーマ

```ruby
create_table "orders", force: :cascade do |t|
  t.bigint "user_id", null: false
  t.string "status", null: false
  t.decimal "total_amount", precision: 10, scale: 2
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
  t.index ["user_id"], name: "index_orders_on_user_id"
end
```

## 補足

- レガシーシステムからのデータ移行により、status カラムには大文字・小文字が混在
- 新規登録時は小文字で保存されるが、移行データは大文字のまま
