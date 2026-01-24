# 既存コードベース情報

## Transaction モデル

```ruby
class Transaction < ApplicationRecord
  belongs_to :account

  # amount は decimal(10, 2) で定義されている
  validates :amount, presence: true, numericality: { greater_than: 0 }
end
```

## スキーマ

```ruby
create_table "transactions", force: :cascade do |t|
  t.bigint "account_id", null: false
  t.decimal "amount", precision: 10, scale: 2, null: false
  t.string "description"
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
  t.index ["account_id"], name: "index_transactions_on_account_id"
end
```

## 補足

- Railsでは decimal 型はデフォルトで BigDecimal として扱われる
- 金額計算では BigDecimal を使用することで精度を保証できる
