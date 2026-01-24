# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  name       :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: carts
#
#  id         :bigint           not null, primary key
#  user_id    :bigint           not null
#  status     :string           default("active")
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: cart_items
#
#  id         :bigint           not null, primary key
#  cart_id    :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          default(1)
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: products
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  price_cents :integer          not null
#  active      :boolean          default(true)
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :carts, dependent: :destroy
  has_one :active_cart, -> { where(status: 'active') }, class_name: 'Cart'

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true

  def current_cart
    active_cart || carts.create!(status: 'active')
  end
end

class Cart < ApplicationRecord
  belongs_to :user
  has_many :cart_items, dependent: :destroy
  has_many :products, through: :cart_items

  validates :status, inclusion: { in: %w[active completed abandoned] }

  scope :active, -> { where(status: 'active') }
  scope :for_user, ->(user) { where(user: user) }

  def total_items
    cart_items.sum(:quantity)
  end

  def total_price_cents
    cart_items.joins(:product).sum('products.price_cents * cart_items.quantity')
  end

  def owned_by?(user)
    self.user == user
  end
end

class CartItem < ApplicationRecord
  belongs_to :cart
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :product_id, uniqueness: { scope: :cart_id }

  scope :for_product, ->(product) { where(product: product) }

  def total_price_cents
    product.price_cents * quantity
  end
end

class Product < ApplicationRecord
  has_many :cart_items, dependent: :destroy

  validates :name, presence: true
  validates :price_cents, presence: true, numericality: { greater_than: 0 }

  scope :active, -> { where(active: true) }

  def price
    Money.new(price_cents)
  end
end
```