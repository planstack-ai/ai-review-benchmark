# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  total_cents  :integer          default(0), not null
#  status       :string           default("pending"), not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: order_items
#
#  id           :bigint           not null, primary key
#  order_id     :bigint           not null
#  product_id   :bigint           not null
#  quantity     :integer          not null
#  price_cents  :integer          not null
#  status       :string           default("active"), not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Indexes
#
#  index_order_items_on_order_id    (order_id)
#  index_order_items_on_product_id  (product_id)
```

## Models

```ruby
class Order < ApplicationRecord
  has_many :order_items, dependent: :destroy
  
  enum status: {
    pending: 'pending',
    confirmed: 'confirmed',
    shipped: 'shipped',
    delivered: 'delivered',
    cancelled: 'cancelled'
  }
  
  monetize :total_cents
  
  scope :active, -> { where.not(status: 'cancelled') }
  
  def calculate_total
    order_items.active.sum { |item| item.quantity * item.price_cents }
  end
  
  def fully_cancelled?
    order_items.all?(&:cancelled?)
  end
  
  def has_active_items?
    order_items.active.exists?
  end
  
  private
  
  def update_total_from_items
    self.total_cents = calculate_total
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product
  
  enum status: {
    active: 'active',
    cancelled: 'cancelled'
  }
  
  monetize :price_cents
  
  scope :active, -> { where(status: 'active') }
  scope :cancelled, -> { where(status: 'cancelled') }
  
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price_cents, presence: true, numericality: { greater_than: 0 }
  
  def line_total_cents
    quantity * price_cents
  end
  
  def cancel!
    update!(status: 'cancelled')
  end
end

class Product < ApplicationRecord
  has_many :order_items
  
  validates :name, presence: true
  validates :price_cents, presence: true, numericality: { greater_than: 0 }
  
  monetize :price_cents
end
```