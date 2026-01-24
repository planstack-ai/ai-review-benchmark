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
#  status       :string           default("pending"), not null
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
#  stock_count   :integer          default(0), not null
#  created_at    :datetime         not null
#  updated_at    :datetime         not null
#
# Table name: audit_logs
#
#  id         :bigint           not null, primary key
#  action     :string           not null
#  details    :text
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
    update!(status: 'confirmed', total_amount: calculate_total)
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

  before_validation :set_price_from_product

  private

  def set_price_from_product
    self.price = product.price if product && price.blank?
  end
end

class Product < ApplicationRecord
  has_many :order_items
  has_many :orders, through: :order_items

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
  validates :stock_count, presence: true, numericality: { greater_than_or_equal_to: 0 }

  scope :in_stock, -> { where('stock_count > 0') }

  def reserve_stock!(quantity)
    raise InsufficientStockError if stock_count < quantity
    decrement!(:stock_count, quantity)
  end

  def release_stock!(quantity)
    increment!(:stock_count, quantity)
  end
end

class AuditLog < ApplicationRecord
  validates :action, presence: true

  def self.log_action(action, details = nil)
    create!(action: action, details: details)
  end
end

class InsufficientStockError < StandardError; end
```