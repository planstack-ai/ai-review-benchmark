# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id                :bigint           not null, primary key
#  user_id           :bigint           not null
#  status            :string           not null
#  subtotal_cents    :integer          not null, default: 0
#  tax_cents         :integer          not null, default: 0
#  shipping_cents    :integer          not null, default: 0
#  total_cents       :integer          not null, default: 0
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
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
# Table name: products
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  price_cents :integer          not null
#  weight_grams :integer         not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  monetize :subtotal_cents
  monetize :tax_cents
  monetize :shipping_cents
  monetize :total_cents

  enum status: {
    pending: 'pending',
    confirmed: 'confirmed',
    shipped: 'shipped',
    delivered: 'delivered',
    cancelled: 'cancelled'
  }

  scope :completed, -> { where(status: ['shipped', 'delivered']) }
  scope :active, -> { where.not(status: 'cancelled') }

  def calculate_subtotal
    order_items.sum { |item| item.quantity * item.price_cents }
  end

  def calculate_tax
    (calculate_subtotal * 0.1).to_i
  end

  def total_weight
    order_items.sum { |item| item.quantity * item.product.weight_grams }
  end

  private

  def update_totals
    self.subtotal_cents = calculate_subtotal
    self.tax_cents = calculate_tax
    self.total_cents = subtotal_cents + tax_cents + shipping_cents
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  monetize :price_cents

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price_cents, presence: true, numericality: { greater_than: 0 }

  def line_total
    quantity * price_cents
  end
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :destroy
  has_many :orders, through: :order_items

  monetize :price_cents

  validates :name, presence: true
  validates :price_cents, presence: true, numericality: { greater_than: 0 }
  validates :weight_grams, presence: true, numericality: { greater_than: 0 }

  scope :available, -> { where(available: true) }
end

class ShippingCalculator
  STANDARD_RATE = 800
  EXPRESS_RATE = 1200
  WEIGHT_THRESHOLD = 2000

  def self.calculate_standard_shipping(weight_grams)
    base_cost = STANDARD_RATE
    base_cost += ((weight_grams - WEIGHT_THRESHOLD) / 500) * 200 if weight_grams > WEIGHT_THRESHOLD
    base_cost
  end

  def self.calculate_express_shipping(weight_grams)
    base_cost = EXPRESS_RATE
    base_cost += ((weight_grams - WEIGHT_THRESHOLD) / 500) * 300 if weight_grams > WEIGHT_THRESHOLD
    base_cost
  end
end
```