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
# Indexes
#
#  index_products_on_sku  (sku) UNIQUE
#

# == Schema Information
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
# Indexes
#
#  index_order_items_on_order_id    (order_id)
#  index_order_items_on_product_id  (product_id)
#

# == Schema Information
#
# Table name: orders
#
#  id         :bigint           not null, primary key
#  status     :string           default("pending"), not null
#  total      :decimal(10,2)    not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
```

## Models

```ruby
class Product < ApplicationRecord
  has_many :order_items, dependent: :destroy
  
  validates :name, presence: true
  validates :sku, presence: true, uniqueness: true
  validates :stock_quantity, presence: true, numericality: { greater_than_or_equal_to: 0 }
  validates :reserved_quantity, presence: true, numericality: { greater_than_or_equal_to: 0 }
  
  scope :in_stock, -> { where('stock_quantity > 0') }
  scope :low_stock, ->(threshold = 10) { where('stock_quantity <= ?', threshold) }
  
  def available_quantity
    stock_quantity - reserved_quantity
  end
  
  def in_stock?(quantity = 1)
    available_quantity >= quantity
  end
  
  def reserve_stock(quantity)
    increment(:reserved_quantity, quantity)
    decrement(:stock_quantity, quantity)
    save!
  end
  
  def release_reserved_stock(quantity)
    decrement(:reserved_quantity, quantity)
    increment(:stock_quantity, quantity)
    save!
  end
end

class Order < ApplicationRecord
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items
  
  validates :status, inclusion: { in: %w[pending confirmed shipped delivered cancelled] }
  validates :total, presence: true, numericality: { greater_than: 0 }
  
  scope :pending, -> { where(status: 'pending') }
  scope :confirmed, -> { where(status: 'confirmed') }
  
  def confirm!
    transaction do
      order_items.includes(:product).each do |item|
        item.product.reserve_stock(item.quantity)
      end
      update!(status: 'confirmed')
    end
  end
  
  def cancel!
    transaction do
      if confirmed?
        order_items.includes(:product).each do |item|
          item.product.release_reserved_stock(item.quantity)
        end
      end
      update!(status: 'cancelled')
    end
  end
  
  private
  
  def confirmed?
    status == 'confirmed'
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product
  
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }
  
  before_create :set_price_from_product
  
  private
  
  def set_price_from_product
    self.price = product.price if product&.price
  end
end
```