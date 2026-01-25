# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: products
#
#  id                :bigint           not null, primary key
#  name              :string           not null
#  base_price        :decimal(10,2)    not null
#  category_id       :bigint           not null
#  tax_rate          :decimal(5,4)     default(0.0)
#  weight            :decimal(8,3)
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#
# Table name: discounts
#
#  id                :bigint           not null, primary key
#  name              :string           not null
#  discount_type     :string           not null
#  value             :decimal(10,2)    not null
#  min_quantity      :integer          default(1)
#  category_id       :bigint
#  active            :boolean          default(true)
#  starts_at         :datetime
#  ends_at           :datetime
#
# Table name: shipping_zones
#
#  id                :bigint           not null, primary key
#  name              :string           not null
#  base_rate         :decimal(8,2)     not null
#  per_kg_rate       :decimal(8,2)     default(0.0)
#  free_shipping_threshold :decimal(10,2)
#
# Table name: categories
#
#  id                :bigint           not null, primary key
#  name              :string           not null
#  markup_percentage :decimal(5,2)     default(0.0)
```

## Models

```ruby
class Product < ApplicationRecord
  belongs_to :category
  has_many :line_items
  
  validates :base_price, presence: true, numericality: { greater_than: 0 }
  validates :weight, presence: true, numericality: { greater_than: 0 }
  
  scope :in_category, ->(category) { where(category: category) }
  scope :with_base_price_between, ->(min, max) { where(base_price: min..max) }
  
  def price_with_markup
    base_price * (1 + (category.markup_percentage / 100))
  end
end

class Category < ApplicationRecord
  has_many :products
  has_many :discounts
  
  validates :markup_percentage, numericality: { greater_than_or_equal_to: 0 }
end

class Discount < ApplicationRecord
  belongs_to :category, optional: true
  
  DISCOUNT_TYPES = %w[percentage fixed_amount].freeze
  
  validates :discount_type, inclusion: { in: DISCOUNT_TYPES }
  validates :value, presence: true, numericality: { greater_than: 0 }
  
  scope :active, -> { where(active: true) }
  scope :current, -> { where('starts_at <= ? AND (ends_at IS NULL OR ends_at >= ?)', Time.current, Time.current) }
  scope :for_category, ->(category) { where(category: [nil, category]) }
  scope :applicable_to_quantity, ->(qty) { where('min_quantity <= ?', qty) }
  
  def percentage?
    discount_type == 'percentage'
  end
  
  def fixed_amount?
    discount_type == 'fixed_amount'
  end
end

class ShippingZone < ApplicationRecord
  validates :base_rate, presence: true, numericality: { greater_than_or_equal_to: 0 }
  validates :per_kg_rate, numericality: { greater_than_or_equal_to: 0 }
  
  def calculate_shipping_cost(total_weight, subtotal = 0)
    return 0 if free_shipping_threshold && subtotal >= free_shipping_threshold
    base_rate + (per_kg_rate * total_weight)
  end
end

class LineItem < ApplicationRecord
  belongs_to :product
  
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :unit_price, presence: true, numericality: { greater_than: 0 }
  
  def total_weight
    quantity * product.weight
  end
  
  def subtotal
    quantity * unit_price
  end
end
```