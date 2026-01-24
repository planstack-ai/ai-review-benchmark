# 既存コードベース

## スキーマ

```ruby
# orders table (数百万レコード)
# - id: bigint
# - user_id: bigint (indexed)
# - status: integer
# - created_at: datetime (indexed)

# order_items table
# - id: bigint
# - order_id: bigint (indexed)
# - product_id: bigint
```

## モデル・サービス

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items

  scope :recent, -> { where('created_at > ?', 30.days.ago) }
  scope :with_items, -> { includes(:order_items) }
  scope :with_user, -> { includes(:user) }
end

# find_each でバッチ処理すること
# includes で N+1 を防ぐこと
```
