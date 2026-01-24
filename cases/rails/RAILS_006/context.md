# 既存コードベース

## スキーマ

```ruby
# orders table
# - id: bigint
# - user_id: bigint
# - status: integer (enum)
# - total: decimal(10,2)
# - created_at: datetime
```

## モデル・サービス

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy

  enum status: { pending: 0, confirmed: 1, shipped: 2 }

  scope :active, -> { where.not(status: :canceled) }
  scope :recent, -> { where('created_at > ?', 7.days.ago) }

  after_commit :notify_user, on: :create

  private

  def notify_user
    OrderMailer.confirmation(self).deliver_later
  end
end
```
