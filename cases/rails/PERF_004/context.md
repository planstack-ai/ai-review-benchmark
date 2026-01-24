# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id          :bigint           not null, primary key
#  user_id     :bigint           not null
#  status      :string           not null
#  total_cents :integer          not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_orders_on_user_id        (user_id)
#  index_orders_on_status         (status)
#  index_orders_on_created_at     (created_at)
#

# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  price_cents :integer         not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_order_items_on_order_id   (order_id)
#  index_order_items_on_product_id (product_id)
#

# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  name       :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
```

## Models

```ruby
class User < ApplicationRecord
  has_many :orders, dependent: :destroy
  
  validates :email, presence: true, uniqueness: true
  validates :name, presence: true
  
  scope :active, -> { joins(:orders).where(orders: { created_at: 30.days.ago.. }).distinct }
end

class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items
  
  validates :status, presence: true, inclusion: { in: %w[pending confirmed shipped delivered cancelled] }
  validates :total_cents, presence: true, numericality: { greater_than: 0 }
  
  scope :pending, -> { where(status: 'pending') }
  scope :confirmed, -> { where(status: 'confirmed') }
  scope :shipped, -> { where(status: 'shipped') }
  scope :delivered, -> { where(status: 'delivered') }
  scope :cancelled, -> { where(status: 'cancelled') }
  scope :completed, -> { where(status: ['delivered', 'shipped']) }
  scope :active, -> { where.not(status: 'cancelled') }
  scope :recent, -> { where(created_at: 30.days.ago..) }
  scope :this_month, -> { where(created_at: Date.current.beginning_of_month..) }
  scope :last_month, -> { where(created_at: 1.month.ago.beginning_of_month..1.month.ago.end_of_month) }
  
  def total_amount
    Money.new(total_cents)
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product
  
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price_cents, presence: true, numericality: { greater_than: 0 }
  
  def price
    Money.new(price_cents)
  end
  
  def total_price
    Money.new(price_cents * quantity)
  end
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :destroy
  has_many :orders, through: :order_items
  
  validates :name, presence: true
  validates :price_cents, presence: true, numericality: { greater_than: 0 }
  
  scope :popular, -> { joins(:order_items).group('products.id').having('COUNT(order_items.id) > 10') }
end
```