# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id                    :bigint           not null, primary key
#  user_id              :bigint           not null
#  subtotal_cents       :integer          default(0), not null
#  discount_cents       :integer          default(0), not null
#  total_cents          :integer          default(0), not null
#  status               :string           default("pending"), not null
#  created_at           :datetime         not null
#  updated_at           :datetime         not null
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  price_cents :integer         not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: discounts
#
#  id              :bigint           not null, primary key
#  code            :string           not null
#  discount_type   :string           not null
#  amount_cents    :integer
#  percentage      :decimal(5,2)
#  active          :boolean          default(true)
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  MINIMUM_ORDER_AMOUNT_CENTS = 100_000 # 1000 yen

  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items
  has_many :applied_discounts, dependent: :destroy
  has_many :discounts, through: :applied_discounts

  monetize :subtotal_cents
  monetize :discount_cents
  monetize :total_cents

  validates :status, inclusion: { in: %w[pending confirmed shipped delivered cancelled] }

  scope :confirmed, -> { where(status: 'confirmed') }
  scope :pending, -> { where(status: 'pending') }

  def calculate_subtotal
    order_items.sum { |item| item.quantity * item.price_cents }
  end

  def calculate_total_discount
    applied_discounts.sum(&:discount_amount_cents)
  end

  def final_amount_cents
    subtotal_cents - discount_cents
  end

  def recalculate_totals!
    self.subtotal_cents = calculate_subtotal
    self.discount_cents = calculate_total_discount
    self.total_cents = final_amount_cents
    save!
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  monetize :price_cents

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price_cents, presence: true, numericality: { greater_than: 0 }

  def total_price_cents
    quantity * price_cents
  end
end

class Discount < ApplicationRecord
  DISCOUNT_TYPES = %w[fixed_amount percentage].freeze

  has_many :applied_discounts, dependent: :destroy
  has_many :orders, through: :applied_discounts

  monetize :amount_cents, allow_nil: true

  validates :discount_type, inclusion: { in: DISCOUNT_TYPES }
  validates :code, presence: true, uniqueness: true
  validates :amount_cents, presence: true, if: -> { discount_type == 'fixed_amount' }
  validates :percentage, presence: true, if: -> { discount_type == 'percentage' }

  scope :active, -> { where(active: true) }

  def calculate_discount_for(order)
    case discount_type
    when 'fixed_amount'
      amount_cents
    when 'percentage'
      (order.subtotal_cents * percentage / 100).to_i
    end
  end
end

class AppliedDiscount < ApplicationRecord
  belongs_to :order
  belongs_to :discount

  monetize :discount_amount_cents

  validates :discount_amount_cents, presence: true, numericality: { greater_than: 0 }
end
```