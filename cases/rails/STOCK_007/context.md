# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  status       :string           not null
#  cancelled_at :datetime
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: products
#
#  id                    :bigint           not null, primary key
#  name                  :string           not null
#  stock_quantity        :integer          default(0), not null
#  reserved_quantity     :integer          default(0), not null
#  created_at            :datetime         not null
#  updated_at            :datetime         not null
#
# Table name: stock_movements
#
#  id           :bigint           not null, primary key
#  product_id   :bigint           not null
#  order_id     :bigint
#  movement_type :string          not null
#  quantity     :integer          not null
#  reference_id :string
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items
  has_many :stock_movements, dependent: :destroy

  enum status: {
    pending: 'pending',
    confirmed: 'confirmed',
    shipped: 'shipped',
    delivered: 'delivered',
    cancelled: 'cancelled'
  }

  scope :cancelled, -> { where(status: 'cancelled') }
  scope :active, -> { where.not(status: 'cancelled') }

  def cancel!
    transaction do
      update!(status: 'cancelled', cancelled_at: Time.current)
      restore_reserved_stock
    end
  end

  private

  def restore_reserved_stock
    # Implementation needed
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }

  def reserve_stock!
    product.reserve_stock!(quantity, order)
  end
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :destroy
  has_many :stock_movements, dependent: :destroy

  validates :stock_quantity, :reserved_quantity, presence: true, 
            numericality: { greater_than_or_equal_to: 0 }

  def available_quantity
    stock_quantity - reserved_quantity
  end

  def reserve_stock!(quantity, order)
    transaction do
      update!(reserved_quantity: reserved_quantity + quantity)
      stock_movements.create!(
        movement_type: 'reservation',
        quantity: -quantity,
        order: order,
        reference_id: "order_#{order.id}"
      )
    end
  end

  def restore_stock!(quantity, order, reference_id)
    transaction do
      update!(reserved_quantity: [reserved_quantity - quantity, 0].max)
      stock_movements.create!(
        movement_type: 'restoration',
        quantity: quantity,
        order: order,
        reference_id: reference_id
      )
    end
  end
end

class StockMovement < ApplicationRecord
  belongs_to :product
  belongs_to :order, optional: true

  MOVEMENT_TYPES = %w[reservation restoration adjustment].freeze

  validates :movement_type, inclusion: { in: MOVEMENT_TYPES }
  validates :quantity, presence: true, numericality: { other_than: 0 }

  scope :reservations, -> { where(movement_type: 'reservation') }
  scope :restorations, -> { where(movement_type: 'restoration') }
  scope :for_order, ->(order) { where(order: order) }
  scope :by_reference, ->(ref) { where(reference_id: ref) }
end
```