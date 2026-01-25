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
# Table name: orders
#
#  id                      :bigint           not null, primary key
#  user_id                 :bigint           not null
#  total_amount            :decimal(10, 2)   not null
#  status                  :string           not null
#  tracking_number         :string
#  estimated_delivery_date :date
#  created_at              :datetime         not null
#  updated_at              :datetime         not null
#
# Table name: order_items
#
#  id          :bigint           not null, primary key
#  order_id    :bigint           not null
#  product_id  :bigint           not null
#  quantity    :integer          not null
#  unit_price  :decimal(10, 2)   not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Table name: products
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  price      :decimal(10, 2)   not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: shipping_addresses
#
#  id           :bigint           not null, primary key
#  order_id     :bigint           not null
#  street       :string           not null
#  city         :string           not null
#  state        :string           not null
#  postal_code  :string           not null
#  country      :string           not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true
end

class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items
  has_one :shipping_address, dependent: :destroy

  validates :total_amount, presence: true, numericality: { greater_than: 0 }
  validates :status, presence: true, inclusion: { in: %w[pending confirmed shipped delivered cancelled] }

  scope :for_user, ->(user) { where(user: user) }
  scope :recent, -> { order(created_at: :desc) }
  scope :by_status, ->(status) { where(status: status) }
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :unit_price, presence: true, numericality: { greater_than: 0 }

  def total_price
    unit_price * quantity
  end
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :restrict_with_error

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
end

class ShippingAddress < ApplicationRecord
  belongs_to :order

  validates :street, :city, :state, :postal_code, :country, presence: true

  def full_address
    "#{street}, #{city}, #{state} #{postal_code}, #{country}"
  end
end
```

## Security Guidelines

When implementing order access:
- **Always scope queries to current user**: Use `current_user.orders.find(order_id)` instead of `Order.find(order_id)`
- Authorization should occur at the database query level, not as a separate check after fetching
- This prevents IDOR (Insecure Direct Object Reference) vulnerabilities and timing attacks
