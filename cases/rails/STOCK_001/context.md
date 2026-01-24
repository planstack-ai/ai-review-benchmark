# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: products
#
#  id                :bigint           not null, primary key
#  name              :string           not null
#  sku               :string           not null
#  stock_quantity    :integer          default(0), not null
#  reserved_quantity :integer          default(0), not null
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#
# Table name: cart_items
#
#  id         :bigint           not null, primary key
#  cart_id    :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: orders
#
#  id         :bigint           not null, primary key
#  user_id    :bigint           not null
#  status     :string           default("pending"), not null
#  total      :decimal(10,2)    not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  price      :decimal(10,2)    not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: stock_reservations
#
#  id         :bigint           not null, primary key
#  product_id :bigint           not null
#  order_id   :bigint           not null
#  quantity   :integer          not null
#  expires_at :datetime         not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class Product < ApplicationRecord
  has_many :cart_items, dependent: :destroy
  has_many :order_items, dependent: :destroy
  has_many :stock_reservations, dependent: :destroy

  validates :name, presence: true
  validates :sku, presence: true, uniqueness: true
  validates :stock_quantity, :reserved_quantity, presence: true, numericality: { greater_than_or_equal_to: 0 }

  scope :in_stock, -> { where('stock_quantity > reserved_quantity') }
  scope :low_stock, ->(threshold = 10) { where('(stock_quantity - reserved_quantity) <= ?', threshold) }

  def available_quantity
    stock_quantity - reserved_quantity
  end

  def can_fulfill?(requested_quantity)
    available_quantity >= requested_quantity
  end

  def reserve_stock!(quantity, order)
    with_lock do
      raise InsufficientStockError unless can_fulfill?(quantity)
      
      increment!(:reserved_quantity, quantity)
      stock_reservations.create!(
        order: order,
        quantity: quantity,
        expires_at: 30.minutes.from_now
      )
    end
  end

  def release_reservation!(reservation)
    with_lock do
      decrement!(:reserved_quantity, reservation.quantity)
      reservation.destroy!
    end
  end
end

class Cart < ApplicationRecord
  belongs_to :user
  has_many :cart_items, dependent: :destroy
  has_many :products, through: :cart_items

  def total_items
    cart_items.sum(:quantity)
  end

  def clear!
    cart_items.destroy_all
  end
end

class CartItem < ApplicationRecord
  belongs_to :cart
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
end

class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items
  has_many :stock_reservations, dependent: :destroy

  enum status: { pending: 'pending', confirmed: 'confirmed', shipped: 'shipped', cancelled: 'cancelled' }

  validates :total, presence: true, numericality: { greater_than: 0 }

  scope :active, -> { where.not(status: 'cancelled') }
  scope :recent, -> { order(created_at: :desc) }
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }
end

class StockReservation < ApplicationRecord
  belongs_to :product
  belongs_to :order

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :expires_at, presence: true

  scope :expired, -> { where('expires_at < ?', Time.current) }
  scope :active, -> { where('expires_at >= ?', Time.current) }

  def expired?
    expires_at < Time.current
  end
end

class InsufficientStockError < StandardError; end
```