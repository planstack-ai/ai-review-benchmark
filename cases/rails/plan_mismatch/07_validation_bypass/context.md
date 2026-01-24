# 既存コードベース情報

## Coupon モデル

```ruby
class Coupon < ApplicationRecord
  has_many :orders

  scope :active, -> { where('expires_at > ?', Time.current) }

  # コードからクーポンを検索
  def self.find_by_code(code)
    find_by(code: code.upcase)
  end

  # 注文に対して有効か検証
  def valid_for?(order)
    !expired? &&
      !usage_limit_reached? &&
      order.subtotal >= minimum_amount &&
      applicable_to_user?(order.user)
  end

  def expired?
    expires_at < Time.current
  end

  def usage_limit_reached?
    usage_limit.present? && usage_count >= usage_limit
  end

  def applicable_to_user?(user)
    first_order_only? ? user.orders.completed.none? : true
  end

  # 割引額を計算
  def discount_amount(order)
    if percentage?
      (order.subtotal * discount_rate / 100).floor
    else
      [fixed_amount, order.subtotal].min
    end
  end
end
```

## Order モデル

```ruby
class Order < ApplicationRecord
  belongs_to :coupon, optional: true

  def apply_coupon(coupon)
    self.coupon = coupon
    self.discount = coupon.discount_amount(self)
  end
end
```
