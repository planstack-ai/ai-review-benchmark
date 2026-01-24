# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: products
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  base_price  :decimal(10,2)    not null
#  tax_rate    :decimal(5,4)     default(0.0)
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#

# Table name: discounts
#
#  id              :bigint           not null, primary key
#  product_id      :bigint           not null
#  percentage      :decimal(5,2)     not null
#  minimum_quantity :integer         default(1)
#  active          :boolean          default(true)
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
#

# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  unit_price :decimal(10,2)    not null
#  total_price :decimal(10,2)   not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
```

## Models

```ruby
class Product < ApplicationRecord
  has_many :discounts, dependent: :destroy
  has_many :order_items, dependent: :destroy

  validates :name, presence: true
  validates :base_price, presence: true, numericality: { greater_than: 0 }
  validates :tax_rate, numericality: { greater_than_or_equal_to: 0, less_than: 1 }

  scope :with_active_discounts, -> { joins(:discounts).where(discounts: { active: true }) }

  CURRENCY_PRECISION = 2
  TAX_PRECISION = 4
  DISCOUNT_PRECISION = 2

  def price_with_tax
    base_price * (1 + tax_rate)
  end

  def applicable_discount(quantity = 1)
    discounts.active
             .where('minimum_quantity <= ?', quantity)
             .order(percentage: :desc)
             .first
  end

  private

  def round_currency(amount)
    amount.round(CURRENCY_PRECISION)
  end
end

class Discount < ApplicationRecord
  belongs_to :product

  validates :percentage, presence: true, 
            numericality: { greater_than: 0, less_than_or_equal_to: 100 }
  validates :minimum_quantity, presence: true, 
            numericality: { greater_than: 0 }

  scope :active, -> { where(active: true) }
  scope :for_quantity, ->(qty) { where('minimum_quantity <= ?', qty) }

  def discount_multiplier
    (100 - percentage) / 100.0
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :unit_price, presence: true, numericality: { greater_than: 0 }
  validates :total_price, presence: true, numericality: { greater_than: 0 }

  before_validation :set_prices, on: :create

  private

  def set_prices
    return unless product && quantity

    self.unit_price = calculate_unit_price
    self.total_price = unit_price * quantity
  end

  def calculate_unit_price
    # Implementation will be provided in the code under review
    raise NotImplementedError, "Price calculation logic needed"
  end
end
```