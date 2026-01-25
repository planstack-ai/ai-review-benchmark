# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id                :bigint           not null, primary key
#  user_id           :bigint           not null
#  status            :string           default("pending")
#  subtotal          :decimal(10,2)
#  tax_amount        :decimal(10,2)
#  shipping_cost     :decimal(10,2)
#  total_amount      :decimal(10,2)
#  payment_status    :string           default("unpaid")
#  payment_reference :string
#  confirmed_at      :datetime
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#
# Indexes
#
#  index_orders_on_user_id  (user_id)
#  index_orders_on_status   (status)
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
#  id             :bigint           not null, primary key
#  name           :string           not null
#  price          :decimal(8,2)     not null
#  stock_quantity :integer          default(0)
#  created_at     :datetime         not null
#  updated_at     :datetime         not null
#

# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  name       :string
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  enum status: { pending: 'pending', confirmed: 'confirmed', shipped: 'shipped', delivered: 'delivered', cancelled: 'cancelled' }
  enum payment_status: { unpaid: 'unpaid', paid: 'paid', refunded: 'refunded' }

  validates :user, presence: true
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :unit_price, presence: true, numericality: { greater_than_or_equal_to: 0 }

  def line_total
    quantity * unit_price
  end
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :destroy

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
  validates :stock_quantity, numericality: { greater_than_or_equal_to: 0 }
end

class User < ApplicationRecord
  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: true
end
```

## External Services

```ruby
class PaymentGateway
  # Charges the given amount using the payment method
  # Returns a result object with success?, transaction_id, error_message
  def self.charge(amount:, payment_method:, customer:)
    # External payment processing
  end
end

class OrderMailer < ApplicationMailer
  def confirmation_email(order)
    @order = order
    mail(to: order.user.email, subject: 'Order Confirmation')
  end
end
```

## Shipping Address

```ruby
class ShippingAddress
  attr_accessor :country, :state, :city, :postal_code

  def international?
    country != 'US'
  end

  def tax_rate
    # Returns state-specific tax rate or nil for default
  end
end
```
