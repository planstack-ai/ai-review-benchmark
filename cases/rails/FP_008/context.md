# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  status       :string           not null
#  total_amount :decimal(10,2)    not null
#  user_id      :bigint           not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Indexes
#
#  index_orders_on_status   (status)
#  index_orders_on_user_id  (user_id)
#

# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  price      :decimal(8,2)     not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#

# Table name: payments
#
#  id              :bigint           not null, primary key
#  order_id        :bigint           not null
#  amount          :decimal(10,2)    not null
#  payment_method  :string           not null
#  status          :string           not null
#  processed_at    :datetime
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
#
```

## Models

```ruby
class User < ApplicationRecord
  has_many :orders, dependent: :destroy
  
  validates :email, presence: true, uniqueness: true
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :destroy
  
  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
  
  scope :available, -> { where(available: true) }
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product
  
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }
  
  def subtotal
    quantity * price
  end
end

class Payment < ApplicationRecord
  belongs_to :order
  
  STATUSES = %w[pending processing completed failed refunded].freeze
  METHODS = %w[credit_card paypal bank_transfer].freeze
  
  validates :amount, presence: true, numericality: { greater_than: 0 }
  validates :payment_method, inclusion: { in: METHODS }
  validates :status, inclusion: { in: STATUSES }
  
  scope :completed, -> { where(status: 'completed') }
  scope :failed, -> { where(status: 'failed') }
  
  def completed?
    status == 'completed'
  end
  
  def failed?
    status == 'failed'
  end
end

class OrderMailer < ApplicationMailer
  def confirmation(order)
    @order = order
    mail(to: @order.user.email, subject: 'Order Confirmation')
  end
  
  def shipped(order)
    @order = order
    mail(to: @order.user.email, subject: 'Order Shipped')
  end
  
  def cancelled(order)
    @order = order
    mail(to: @order.user.email, subject: 'Order Cancelled')
  end
end

class InventoryService
  def self.reserve_items(order_items)
    order_items.each do |item|
      product = item.product
      return false unless product.stock_quantity >= item.quantity
    end
    
    order_items.each do |item|
      item.product.decrement!(:stock_quantity, item.quantity)
    end
    
    true
  end
  
  def self.release_items(order_items)
    order_items.each do |item|
      item.product.increment!(:stock_quantity, item.quantity)
    end
  end
end

class ShippingService
  def self.create_shipment(order)
    # External API call to shipping provider
    response = ShippingAPI.create_shipment(
      order_id: order.id,
      items: order.order_items.map(&:to_shipping_hash),
      address: order.shipping_address
    )
    
    response.success?
  end
end
```