# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  has_many :sent_transfers, class_name: "Transfer", foreign_key: :sender_id
  has_many :received_transfers, class_name: "Transfer", foreign_key: :receiver_id

  def withdraw(amount)
    raise InsufficientBalanceError if balance < amount
    decrement!(:balance, amount)
  end

  def deposit(amount)
    increment!(:balance, amount)
  end
end
```

## Transfer モデル

```ruby
class Transfer < ApplicationRecord
  belongs_to :sender, class_name: "User"
  belongs_to :receiver, class_name: "User"

  validates :amount, presence: true, numericality: { greater_than: 0 }
end
```

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "name", null: false
  t.decimal "balance", precision: 10, scale: 2, default: 0
end

create_table "transfers", force: :cascade do |t|
  t.bigint "sender_id", null: false
  t.bigint "receiver_id", null: false
  t.decimal "amount", precision: 10, scale: 2, null: false
  t.datetime "created_at", null: false
end
```
