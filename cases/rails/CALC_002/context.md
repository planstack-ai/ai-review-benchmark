# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  subtotal     :decimal(10, 2)   not null
#  discount     :decimal(10, 2)   default(0.0)
#  tax_rate     :decimal(5, 4)    default(0.1000)
#  total        :decimal(10, 2)
#  status       :string           default("pending")
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  unit_price :decimal(8, 2)    not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: products
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  price       :decimal(8, 2)    not null
#  taxable     :boolean          default(true)
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  validates :subtotal, presence: true, numericality: { greater_than: 0 }
  validates :discount, numericality: { greater_than_or_equal_to: 0 }
  validates :tax_rate, numericality: { greater_than_or_equal_to: 0 }

  scope :completed, -> { where(status: 'completed') }
  scope :with_tax, -> { where('tax_rate > 0') }

  before_save :calculate_subtotal
  before_save :ensure_discount_not_greater_than_subtotal

  def discounted_amount
    subtotal - discount
  end

  def taxable_amount
    return 0 if discounted_amount <= 0
    discounted_amount
  end

  def tax_amount
    (taxable_amount * tax_rate).round(2)
  end

  private

  def calculate_subtotal
    self.subtotal = order_items.sum { |item| item.quantity * item.unit_price }
  end

  def ensure_discount_not_greater_than_subtotal
    self.discount = [discount, subtotal].min
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :unit_price, presence: true, numericality: { greater_than: 0 }

  def line_total
    quantity * unit_price
  end
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :restrict_with_error
  has_many :orders, through: :order_items

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }

  scope :taxable, -> { where(taxable: true) }
  scope :non_taxable, -> { where(taxable: false) }
end
```