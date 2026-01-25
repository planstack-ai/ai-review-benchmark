# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id              :bigint           not null, primary key
#  user_id         :bigint           not null
#  status          :string           default("pending"), not null
#  total_amount    :decimal(10,2)    not null
#  discount_amount :decimal(10,2)    default(0.0)
#  final_amount    :decimal(10,2)
#  order_number    :string           not null
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  unit_price :decimal(8,2)     not null
#  total_price :decimal(8,2)    not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: inventory_items
#
#  id         :bigint           not null, primary key
#  product_id :bigint           not null
#  quantity   :integer          not null
#  reserved   :integer          default(0)
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :orders, dependent: :destroy
  
  def premium?
    subscription_tier == 'premium'
  end
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :destroy
  has_one :inventory_item, dependent: :destroy
  
  scope :active, -> { where(active: true) }
  
  def available_quantity
    inventory_item&.quantity || 0
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product
  
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :unit_price, presence: true, numericality: { greater_than: 0 }
  
  def calculate_total_price
    quantity * unit_price
  end
end

class InventoryItem < ApplicationRecord
  belongs_to :product
  
  def available_for_reservation
    quantity - reserved
  end
  
  def reserve_quantity(amount)
    return false if available_for_reservation < amount
    
    update(reserved: reserved + amount)
  end
  
  def release_reservation(amount)
    update(reserved: [reserved - amount, 0].max)
  end
end

class DiscountService
  def self.calculate_discount(user, total_amount)
    return 0 unless user.premium?
    
    case total_amount
    when 0..99.99
      total_amount * 0.05
    when 100..499.99
      total_amount * 0.10
    else
      total_amount * 0.15
    end
  end
end

class OrderNumberGenerator
  def self.generate
    "ORD-#{Time.current.strftime('%Y%m%d')}-#{SecureRandom.hex(4).upcase}"
  end
end

class NotificationService
  def self.send_order_confirmation(order)
    # Email notification logic
    Rails.logger.info "Order confirmation sent for order #{order.order_number}"
  end
end
```