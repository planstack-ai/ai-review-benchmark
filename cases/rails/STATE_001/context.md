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
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  VALID_STATUSES = %w[
    pending
    confirmed
    processing
    shipped
    delivered
    cancelled
    refunded
  ].freeze

  ALLOWED_TRANSITIONS = {
    'pending' => %w[confirmed cancelled],
    'confirmed' => %w[processing cancelled],
    'processing' => %w[shipped cancelled],
    'shipped' => %w[delivered],
    'delivered' => %w[refunded],
    'cancelled' => [],
    'refunded' => []
  }.freeze

  validates :status, inclusion: { in: VALID_STATUSES }
  validates :total_amount, presence: true, numericality: { greater_than: 0 }

  scope :by_status, ->(status) { where(status: status) }
  scope :active, -> { where.not(status: %w[cancelled refunded]) }
  scope :completed, -> { where(status: %w[delivered refunded]) }

  def pending?
    status == 'pending'
  end

  def confirmed?
    status == 'confirmed'
  end

  def cancelled?
    status == 'cancelled'
  end

  def can_be_cancelled?
    %w[pending confirmed processing].include?(status)
  end

  def final_status?
    %w[delivered cancelled refunded].include?(status)
  end

  private

  def calculate_total
    order_items.sum { |item| item.quantity * item.price }
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }
end

class Product < ApplicationRecord
  has_many :order_items
  has_many :orders, through: :order_items

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
end

class User < ApplicationRecord
  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: true
end
```