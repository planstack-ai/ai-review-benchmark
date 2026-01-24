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
#  tax_amount   :decimal(10,2)    default(0.0)
#  discount     :decimal(10,2)    default(0.0)
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#  user_id      :bigint           not null
#

# Table name: order_items
#
#  id         :bigint           not null, primary key
#  quantity   :integer          not null
#  price      :decimal(8,2)     not null
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#

# Table name: inventory_items
#
#  id              :bigint           not null, primary key
#  product_id      :bigint           not null
#  quantity        :integer          not null
#  reserved_count  :integer          default(0)
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
#
```

## Models

```ruby
class Order < ApplicationRecord
  STATUSES = %w[pending confirmed processing shipped delivered cancelled].freeze
  TAX_RATE = 0.08

  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  validates :status, inclusion: { in: STATUSES }
  validates :total_amount, presence: true, numericality: { greater_than: 0 }

  scope :pending, -> { where(status: 'pending') }
  scope :confirmed, -> { where(status: 'confirmed') }
  scope :cancelled, -> { where(status: 'cancelled') }

  def subtotal
    order_items.sum { |item| item.quantity * item.price }
  end

  def calculate_tax
    subtotal * TAX_RATE
  end

  def calculate_total
    subtotal + tax_amount - discount
  end

  def reserve_inventory!
    order_items.each(&:reserve_inventory!)
  end

  def release_inventory!
    order_items.each(&:release_inventory!)
  end

  def send_confirmation_email
    OrderMailer.confirmation(self).deliver_later
  end

  def log_status_change
    Rails.logger.info "Order #{id} status changed to #{status}"
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }

  def reserve_inventory!
    inventory_item = product.inventory_item
    inventory_item.increment!(:reserved_count, quantity)
  end

  def release_inventory!
    inventory_item = product.inventory_item
    inventory_item.decrement!(:reserved_count, quantity)
  end
end

class Product < ApplicationRecord
  has_one :inventory_item, dependent: :destroy
  has_many :order_items, dependent: :destroy

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }

  def available_quantity
    inventory_item&.quantity || 0
  end
end

class InventoryItem < ApplicationRecord
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than_or_equal_to: 0 }
  validates :reserved_count, presence: true, numericality: { greater_than_or_equal_to: 0 }

  def available_count
    quantity - reserved_count
  end
end
```