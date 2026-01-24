# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  user_id      :bigint           not null
#  status       :string           default("pending")
#  subtotal     :decimal(10,2)
#  tax_amount   :decimal(10,2)
#  total        :decimal(10,2)
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  unit_price :decimal(10,2)    not null
#  total      :decimal(10,2)
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: products
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  price       :decimal(10,2)    not null
#  tax_rate    :decimal(5,4)     default(0.0875)
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  validates :status, inclusion: { in: %w[pending confirmed shipped delivered cancelled] }
  validates :subtotal, :tax_amount, :total, presence: true, numericality: { greater_than_or_equal_to: 0 }

  scope :pending, -> { where(status: 'pending') }
  scope :confirmed, -> { where(status: 'confirmed') }

  CURRENCY_PRECISION = 2
  DEFAULT_TAX_RATE = BigDecimal('0.0875')

  def recalculate_totals!
    update!(
      subtotal: calculate_subtotal,
      tax_amount: calculate_tax_amount,
      total: calculate_total
    )
  end

  private

  def calculate_subtotal
    order_items.sum(&:total)
  end

  def calculate_tax_amount
    order_items.sum { |item| item.calculate_tax }
  end

  def calculate_total
    subtotal + tax_amount
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :unit_price, presence: true, numericality: { greater_than: 0 }

  before_save :calculate_item_total

  def calculate_tax
    tax_rate = product.tax_rate || Order::DEFAULT_TAX_RATE
    (total * tax_rate).round(Order::CURRENCY_PRECISION)
  end

  private

  def calculate_item_total
    self.total = (unit_price * quantity).round(Order::CURRENCY_PRECISION)
  end
end

class Product < ApplicationRecord
  has_many :order_items
  has_many :orders, through: :order_items

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
  validates :tax_rate, numericality: { greater_than_or_equal_to: 0, less_than: 1 }

  scope :taxable, -> { where('tax_rate > 0') }
  scope :tax_exempt, -> { where(tax_rate: 0) }
end
```