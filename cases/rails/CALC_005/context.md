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
#  category    :string
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#

# == Schema Information
#
# Table name: orders
#
#  id          :bigint           not null, primary key
#  user_id     :bigint           not null
#  subtotal    :decimal(10,2)    not null
#  tax_amount  :decimal(10,2)    not null
#  total       :decimal(10,2)    not null
#  status      :string           default("pending")
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#

# == Schema Information
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  unit_price :decimal(10,2)    not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
```

## Models

```ruby
class Product < ApplicationRecord
  validates :name, presence: true
  validates :base_price, presence: true, numericality: { greater_than: 0 }
  
  has_many :order_items, dependent: :destroy
  
  scope :active, -> { where(active: true) }
  scope :by_category, ->(category) { where(category: category) }
  
  def formatted_price
    "$#{base_price.to_f}"
  end
end

class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items
  
  validates :subtotal, :tax_amount, :total, presence: true,
            numericality: { greater_than_or_equal_to: 0 }
  
  enum status: { pending: 'pending', confirmed: 'confirmed', shipped: 'shipped' }
  
  scope :recent, -> { order(created_at: :desc) }
  scope :completed, -> { where(status: ['confirmed', 'shipped']) }
  
  def item_count
    order_items.sum(:quantity)
  end
  
  def calculate_totals
    self.subtotal = order_items.sum { |item| item.quantity * item.unit_price }
    self.tax_amount = calculate_tax
    self.total = subtotal + tax_amount
  end
  
  private
  
  def calculate_tax
    # Implementation needed
    0
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product
  
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :unit_price, presence: true, numericality: { greater_than: 0 }
  
  before_validation :set_unit_price, on: :create
  
  def line_total
    quantity * unit_price
  end
  
  private
  
  def set_unit_price
    self.unit_price = product.base_price if product
  end
end

class User < ApplicationRecord
  has_many :orders, dependent: :destroy
  
  validates :email, presence: true, uniqueness: true
  
  def recent_orders
    orders.recent.limit(10)
  end
end
```