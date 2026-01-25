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
# Table name: payments
#
#  id               :bigint           not null, primary key
#  order_id         :bigint           not null
#  amount           :decimal(10,2)    not null
#  payment_method   :string           not null
#  external_id      :string
#  status           :string           default("pending"), not null
#  created_at       :datetime         not null
#  updated_at       :datetime         not null
#
# Table name: inventory_items
#
#  id         :bigint           not null, primary key
#  sku        :string           not null
#  quantity   :integer          default(0), not null
#  reserved   :integer          default(0), not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :payments, dependent: :destroy
  has_many :order_items, dependent: :destroy

  enum status: {
    pending: 'pending',
    confirmed: 'confirmed',
    processing: 'processing',
    shipped: 'shipped',
    delivered: 'delivered',
    cancelled: 'cancelled'
  }

  scope :recent, -> { where(created_at: 1.week.ago..) }
  scope :by_status, ->(status) { where(status: status) }

  def total_paid
    payments.successful.sum(:amount)
  end

  def fully_paid?
    total_paid >= total_amount
  end
end

class Payment < ApplicationRecord
  belongs_to :order

  enum status: {
    pending: 'pending',
    processing: 'processing',
    successful: 'successful',
    failed: 'failed',
    refunded: 'refunded'
  }

  scope :successful, -> { where(status: 'successful') }
  scope :failed, -> { where(status: 'failed') }

  validates :amount, presence: true, numericality: { greater_than: 0 }
  validates :payment_method, presence: true
end

class InventoryItem < ApplicationRecord
  validates :sku, presence: true, uniqueness: true
  validates :quantity, :reserved, presence: true, numericality: { greater_than_or_equal_to: 0 }

  scope :available, -> { where('quantity > reserved') }
  scope :by_sku, ->(sku) { where(sku: sku) }

  def available_quantity
    quantity - reserved
  end

  def reserve!(amount)
    raise InsufficientInventoryError if available_quantity < amount
    increment!(:reserved, amount)
  end

  def release_reservation!(amount)
    decrement!(:reserved, [amount, reserved].min)
  end
end

class User < ApplicationRecord
  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: true
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :inventory_item, foreign_key: :sku, primary_key: :sku

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }
end

class InsufficientInventoryError < StandardError; end
class PaymentProcessingError < StandardError; end
```
