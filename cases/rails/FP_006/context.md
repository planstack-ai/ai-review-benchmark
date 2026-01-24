# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  user_id      :bigint           not null
#  total_amount :decimal(10,2)    not null
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
#  price      :decimal(8,2)     not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: products
#
#  id            :bigint           not null, primary key
#  name          :string           not null
#  price         :decimal(8,2)     not null
#  stock_count   :integer          default(0)
#  created_at    :datetime         not null
#  updated_at    :datetime         not null
#
# Table name: inventory_logs
#
#  id         :bigint           not null, primary key
#  product_id :bigint           not null
#  change     :integer          not null
#  reason     :string           not null
#  created_at :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  validates :total_amount, presence: true, numericality: { greater_than: 0 }
  validates :status, inclusion: { in: %w[pending confirmed shipped delivered cancelled] }

  scope :pending, -> { where(status: 'pending') }
  scope :confirmed, -> { where(status: 'confirmed') }

  def calculate_total
    order_items.sum { |item| item.quantity * item.price }
  end

  def confirm!
    update!(status: 'confirmed')
  end

  def cancel!
    update!(status: 'cancelled')
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }

  def total_price
    quantity * price
  end
end

class Product < ApplicationRecord
  has_many :order_items
  has_many :inventory_logs

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
  validates :stock_count, numericality: { greater_than_or_equal_to: 0 }

  scope :in_stock, -> { where('stock_count > 0') }
  scope :low_stock, -> { where('stock_count < 10') }

  def available?(quantity)
    stock_count >= quantity
  end

  def reserve_stock!(quantity, reason = 'order_reservation')
    raise InsufficientStockError unless available?(quantity)
    
    decrement!(:stock_count, quantity)
    log_inventory_change(-quantity, reason)
  end

  def release_stock!(quantity, reason = 'order_cancellation')
    increment!(:stock_count, quantity)
    log_inventory_change(quantity, reason)
  end

  private

  def log_inventory_change(change, reason)
    inventory_logs.create!(change: change, reason: reason)
  end
end

class InventoryLog < ApplicationRecord
  belongs_to :product

  validates :change, presence: true
  validates :reason, presence: true

  scope :recent, -> { order(created_at: :desc) }
  scope :for_reason, ->(reason) { where(reason: reason) }
end

class InsufficientStockError < StandardError; end
```