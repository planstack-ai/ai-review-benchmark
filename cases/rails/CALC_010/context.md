# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  customer_id  :bigint           not null
#  status       :string           default("pending")
#  total_cents  :integer          default(0)
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: order_items
#
#  id           :bigint           not null, primary key
#  order_id     :bigint           not null
#  product_id   :bigint           not null
#  quantity     :integer          not null
#  unit_price_cents :integer      not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: products
#
#  id           :bigint           not null, primary key
#  name         :string           not null
#  price_cents  :integer          not null
#  max_quantity :integer          default(1000)
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :customer
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  validates :status, inclusion: { in: %w[pending confirmed shipped delivered cancelled] }
  validates :total_cents, numericality: { greater_than_or_equal_to: 0 }

  scope :bulk_orders, -> { joins(:order_items).group('orders.id').having('SUM(order_items.quantity) >= ?', BULK_THRESHOLD) }
  scope :pending, -> { where(status: 'pending') }

  BULK_THRESHOLD = 100
  MAX_TOTAL_CENTS = 2_147_483_647 # PostgreSQL integer limit

  def bulk_order?
    total_quantity >= BULK_THRESHOLD
  end

  def total_quantity
    order_items.sum(:quantity)
  end

  private

  def calculate_total
    order_items.sum { |item| item.quantity * item.unit_price_cents }
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :unit_price_cents, presence: true, numericality: { greater_than: 0 }

  before_validation :set_unit_price, on: :create

  def line_total_cents
    quantity * unit_price_cents
  end

  private

  def set_unit_price
    self.unit_price_cents = product.price_cents if product
  end
end

class Product < ApplicationRecord
  has_many :order_items
  has_many :orders, through: :order_items

  validates :name, presence: true
  validates :price_cents, presence: true, numericality: { greater_than: 0 }
  validates :max_quantity, numericality: { greater_than: 0 }

  scope :available, -> { where('max_quantity > 0') }

  def price
    Money.new(price_cents)
  end
end
```