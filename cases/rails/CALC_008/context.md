# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  user_id      :bigint           not null
#  subtotal     :decimal(10, 2)   not null
#  discount     :decimal(10, 2)   default(0.0)
#  total        :decimal(10, 2)   not null
#  status       :string           default("pending")
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: coupons
#
#  id              :bigint           not null, primary key
#  code            :string           not null
#  discount_type   :string           not null
#  discount_value  :decimal(10, 2)   not null
#  min_order_value :decimal(10, 2)   default(0.0)
#  max_discount    :decimal(10, 2)
#  active          :boolean          default(true)
#  expires_at      :datetime
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
#
# Table name: order_coupons
#
#  id        :bigint           not null, primary key
#  order_id  :bigint           not null
#  coupon_id :bigint           not null
#  applied   :boolean          default(false)
#  created_at :datetime        not null
#  updated_at :datetime        not null
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :order_coupons, dependent: :destroy
  has_many :coupons, through: :order_coupons

  validates :subtotal, :total, presence: true, numericality: { greater_than: 0 }
  validates :discount, numericality: { greater_than_or_equal_to: 0 }

  scope :completed, -> { where(status: 'completed') }
  scope :pending, -> { where(status: 'pending') }

  def calculate_subtotal
    order_items.sum { |item| item.quantity * item.price }
  end

  def eligible_for_coupon?(coupon)
    return false unless coupon.active?
    return false if coupon.expired?
    return false if subtotal < coupon.min_order_value
    true
  end

  private

  def update_totals
    self.subtotal = calculate_subtotal
    self.total = subtotal - discount
  end
end

class Coupon < ApplicationRecord
  DISCOUNT_TYPES = %w[percentage fixed_amount].freeze

  has_many :order_coupons, dependent: :destroy
  has_many :orders, through: :order_coupons

  validates :code, presence: true, uniqueness: true
  validates :discount_type, inclusion: { in: DISCOUNT_TYPES }
  validates :discount_value, presence: true, numericality: { greater_than: 0 }

  scope :active, -> { where(active: true) }
  scope :unexpired, -> { where('expires_at IS NULL OR expires_at > ?', Time.current) }
  scope :available, -> { active.unexpired }

  def expired?
    expires_at.present? && expires_at < Time.current
  end

  def calculate_discount(order_subtotal)
    case discount_type
    when 'percentage'
      discount = (order_subtotal * discount_value / 100).round(2)
    when 'fixed_amount'
      discount = discount_value
    end

    return 0 if discount.negative?
    return max_discount if max_discount.present? && discount > max_discount
    [discount, order_subtotal].min
  end
end

class OrderCoupon < ApplicationRecord
  belongs_to :order
  belongs_to :coupon

  validates :order_id, uniqueness: { scope: :coupon_id }
  
  scope :applied, -> { where(applied: true) }
end
```