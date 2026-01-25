# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id             :bigint           not null, primary key
#  customer_id    :bigint           not null
#  status         :string           default("pending")
#  subtotal       :decimal(15, 2)   default(0)
#  discount       :decimal(15, 2)   default(0)
#  tax            :decimal(15, 2)   default(0)
#  total          :decimal(15, 2)   default(0)
#  created_at     :datetime         not null
#  updated_at     :datetime         not null
#
# Table name: order_items
#
#  id           :bigint           not null, primary key
#  order_id     :bigint           not null
#  product_id   :bigint           not null
#  quantity     :integer          not null
#  unit_price   :decimal(10, 2)   not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: products
#
#  id           :bigint           not null, primary key
#  name         :string           not null
#  price        :decimal(10, 2)   not null
#  max_quantity :integer          default(1000000)
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

  BULK_THRESHOLD = 100
  HIGH_VALUE_THRESHOLD = 10000

  def bulk_order?
    total_quantity >= BULK_THRESHOLD || subtotal >= HIGH_VALUE_THRESHOLD
  end

  def total_quantity
    order_items.sum(:quantity)
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0, less_than_or_equal_to: 1_000_000 }
  validates :unit_price, presence: true, numericality: { greater_than: 0 }

  def line_total
    unit_price * quantity
  end
end

class Product < ApplicationRecord
  has_many :order_items
  has_many :orders, through: :order_items

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
  validates :max_quantity, numericality: { greater_than: 0 }
end
```

## Business Rules

- **Bulk discount eligibility**: Orders with 100+ items OR subtotal >= $10,000 qualify for additional bulk discounts
- **Bulk discount multiplier**: 15% extra discount on top of regular percentage discount
- **Tax rate**: Standard 8% tax rate applied after discounts
- **Maximum quantity**: System supports up to 1,000,000 units per order item for large B2B transactions

## Calculation Guidelines

When performing arithmetic with large quantities:
- Use `BigDecimal` for precise decimal calculations
- Guard against integer overflow when multiplying large quantities by prices
- Ensure intermediate calculation results don't exceed numeric type limits
