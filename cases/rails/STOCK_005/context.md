# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  status       :string           not null
#  total_amount :decimal(10,2)    not null, default(0.0)
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#  user_id      :bigint           not null
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  quantity   :integer          not null
#  unit_price :decimal(8,2)     not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#  order_id   :bigint           not null
#  product_id :bigint           not null
#
# Table name: products
#
#  id               :bigint           not null, primary key
#  name             :string           not null
#  price            :decimal(8,2)     not null
#  stock_quantity   :integer          not null, default(0)
#  active           :boolean          not null, default(true)
#  created_at       :datetime         not null
#  updated_at       :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  VALID_STATUSES = %w[pending confirmed shipped delivered cancelled].freeze

  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  validates :status, inclusion: { in: VALID_STATUSES }
  validates :total_amount, presence: true, numericality: { greater_than_or_equal_to: 0 }

  scope :pending, -> { where(status: 'pending') }
  scope :confirmed, -> { where(status: 'confirmed') }

  def calculate_total
    order_items.sum { |item| item.quantity * item.unit_price }
  end

  def confirm!
    update!(status: 'confirmed', total_amount: calculate_total)
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :unit_price, presence: true, numericality: { greater_than: 0 }

  before_validation :set_unit_price, on: :create

  def line_total
    quantity * unit_price
  end

  private

  def set_unit_price
    self.unit_price = product.price if product.present?
  end
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :restrict_with_error

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
  validates :stock_quantity, presence: true, numericality: { greater_than_or_equal_to: 0 }

  scope :active, -> { where(active: true) }
  scope :in_stock, -> { where('stock_quantity > 0') }
  scope :available, -> { active.in_stock }

  def available?
    active? && stock_quantity > 0
  end

  def sufficient_stock?(requested_quantity)
    stock_quantity >= requested_quantity
  end
end
```