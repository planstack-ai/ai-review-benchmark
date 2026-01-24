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
# Table name: cart_items
#
#  id         :bigint           not null, primary key
#  cart_id    :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_cart_items_on_cart_id     (cart_id)
#  index_cart_items_on_product_id  (product_id)
#

# == Schema Information
#
# Table name: carts
#
#  id         :bigint           not null, primary key
#  user_id    :bigint
#  status     :string           default("active")
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
```

## Models

```ruby
class Product < ApplicationRecord
  has_many :cart_items, dependent: :destroy
  
  validates :name, presence: true
  validates :sku, presence: true, uniqueness: true
  validates :stock_quantity, :reserved_quantity, presence: true, numericality: { greater_than_or_equal_to: 0 }
  
  scope :in_stock, -> { where('stock_quantity > reserved_quantity') }
  scope :low_stock, ->(threshold = 5) { where('(stock_quantity - reserved_quantity) <= ?', threshold) }
  
  def available_quantity
    stock_quantity - reserved_quantity
  end
  
  def sufficient_stock?(requested_quantity)
    available_quantity >= requested_quantity
  end
  
  def reserve_stock!(quantity)
    return false unless sufficient_stock?(quantity)
    
    increment!(:reserved_quantity, quantity)
    true
  end
  
  def release_stock!(quantity)
    decrement!(:reserved_quantity, [quantity, reserved_quantity].min)
  end
end

class Cart < ApplicationRecord
  belongs_to :user, optional: true
  has_many :cart_items, dependent: :destroy
  has_many :products, through: :cart_items
  
  enum status: { active: 'active', checked_out: 'checked_out', abandoned: 'abandoned' }
  
  scope :active, -> { where(status: 'active') }
  scope :stale, -> { where('updated_at < ?', 1.hour.ago) }
  
  def total_items
    cart_items.sum(:quantity)
  end
  
  def empty?
    cart_items.empty?
  end
end

class CartItem < ApplicationRecord
  belongs_to :cart
  belongs_to :product
  
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :product_id, uniqueness: { scope: :cart_id }
  
  scope :with_products, -> { includes(:product) }
  
  def total_requested_quantity
    quantity
  end
  
  def product_available_quantity
    product.available_quantity
  end
end
```