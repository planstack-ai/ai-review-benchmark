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
#  status       :string           not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Indexes
#
#  index_orders_on_user_id                    (user_id)
#  index_orders_on_status_and_created_at      (status, created_at)
#  index_orders_on_created_at                 (created_at)
#

# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  unit_price :decimal(8,2)     not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_order_items_on_order_id    (order_id)
#  index_order_items_on_product_id  (product_id)
#

# Table name: products
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  category_id :bigint           not null
#  price       :decimal(8,2)     not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_products_on_category_id  (category_id)
#
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  enum status: {
    pending: 'pending',
    processing: 'processing',
    shipped: 'shipped',
    delivered: 'delivered',
    cancelled: 'cancelled'
  }

  scope :recent, -> { where(created_at: 30.days.ago..) }
  scope :completed, -> { where(status: ['shipped', 'delivered']) }
  scope :by_date_range, ->(start_date, end_date) { where(created_at: start_date..end_date) }

  def self.revenue_by_month(year)
    where(created_at: Date.new(year).beginning_of_year..Date.new(year).end_of_year)
      .completed
      .group("DATE_TRUNC('month', created_at)")
      .sum(:total_amount)
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :unit_price, presence: true, numericality: { greater_than: 0 }

  def line_total
    quantity * unit_price
  end
end

class Product < ApplicationRecord
  belongs_to :category
  has_many :order_items, dependent: :destroy
  has_many :orders, through: :order_items

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }

  scope :by_category, ->(category_id) { where(category_id: category_id) }
  scope :price_range, ->(min, max) { where(price: min..max) }

  def self.top_selling(limit = 10)
    joins(:order_items)
      .group('products.id')
      .order('SUM(order_items.quantity) DESC')
      .limit(limit)
  end
end

class Category < ApplicationRecord
  has_many :products, dependent: :destroy

  validates :name, presence: true, uniqueness: true
end

class User < ApplicationRecord
  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: true

  def total_spent
    orders.completed.sum(:total_amount)
  end

  def order_count
    orders.count
  end
end
```