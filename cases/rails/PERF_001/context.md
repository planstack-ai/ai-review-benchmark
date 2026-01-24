# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id          :bigint           not null, primary key
#  user_id     :bigint           not null
#  total_cents :integer          default(0), not null
#  status      :string           default("pending"), not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_orders_on_user_id  (user_id)
#

# == Schema Information
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          default(1), not null
#  price_cents :integer         not null
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
# Table name: products
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  description :text
#  price_cents :integer          not null
#  sku         :string           not null
#  active      :boolean          default(true), not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_products_on_sku     (sku) UNIQUE
#  index_products_on_active  (active)
#
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  enum status: { pending: 'pending', confirmed: 'confirmed', shipped: 'shipped', delivered: 'delivered' }

  scope :recent, -> { order(created_at: :desc) }
  scope :with_items, -> { joins(:order_items) }

  def total_amount
    Money.new(total_cents)
  end

  def item_count
    order_items.sum(:quantity)
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price_cents, presence: true, numericality: { greater_than: 0 }

  scope :by_quantity, -> { order(:quantity) }

  def price
    Money.new(price_cents)
  end

  def line_total
    Money.new(price_cents * quantity)
  end
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :restrict_with_error
  has_many :orders, through: :order_items

  validates :name, presence: true
  validates :sku, presence: true, uniqueness: true
  validates :price_cents, presence: true, numericality: { greater_than: 0 }

  scope :active, -> { where(active: true) }
  scope :by_name, -> { order(:name) }

  def price
    Money.new(price_cents)
  end

  def display_name
    "#{name} (#{sku})"
  end
end

class User < ApplicationRecord
  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: true

  def recent_orders(limit = 10)
    orders.recent.limit(limit)
  end
end
```