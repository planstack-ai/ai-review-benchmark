# 既存コードベース情報

## Order モデル

```ruby
class Order < ApplicationRecord
  has_many :order_items
  belongs_to :user

  enum status: {
    pending: 0,     # 注文受付
    confirmed: 1,   # 確定
    shipped: 2,     # 発送済み
    delivered: 3,   # 配達完了
    cancelled: 4    # キャンセル
  }

  CANCELLABLE_STATUSES = %w[pending confirmed].freeze

  def self.cancellable_statuses
    CANCELLABLE_STATUSES
  end

  # キャンセル可能か判定
  def cancellable?
    CANCELLABLE_STATUSES.include?(status)
  end

  # キャンセル処理
  def cancel!
    raise OrderNotCancellableError unless cancellable?

    transaction do
      restore_stock!
      cancelled!
    end
  end

  private

  def restore_stock!
    order_items.each do |item|
      item.product.increment!(:stock, item.quantity)
    end
  end
end

class OrderNotCancellableError < StandardError; end
```
