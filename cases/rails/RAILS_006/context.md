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
#  active     :boolean          default(true)
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  user_id      :bigint           not null
#  product_id   :bigint           not null
#  quantity     :integer          not null
#  address      :text             not null
#  total_amount :decimal(10, 2)   not null
#  status       :string           default("pending"), not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: products
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  price      :decimal(10, 2)   not null
#  available  :boolean          default(true)
#  stock      :integer          default(0)
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true

  scope :active, -> { where(active: true) }

  def active?
    active
  end
end

class Order < ApplicationRecord
  STATUSES = %w[pending paid shipped delivered cancelled].freeze

  belongs_to :user
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :address, presence: true
  validates :total_amount, presence: true, numericality: { greater_than: 0 }
  validates :status, inclusion: { in: STATUSES }

  scope :pending, -> { where(status: 'pending') }
  scope :paid, -> { where(status: 'paid') }

  def paid?
    status == 'paid'
  end
end

class Product < ApplicationRecord
  has_many :orders, dependent: :restrict_with_error

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }

  scope :available, -> { where(available: true) }

  def available?
    available && stock > 0
  end
end
```

## Services

```ruby
class PaymentService
  def initialize(order)
    @order = order
  end

  def process
    # Payment processing logic
    @order.update!(status: 'paid')
  end
end

class InventoryService
  def initialize(product, quantity)
    @product = product
    @quantity = quantity
  end

  def decrement
    @product.decrement!(:stock, @quantity)
  end
end
```

## Mailers

```ruby
class OrderMailer < ApplicationMailer
  def confirmation_email(order)
    @order = order
    mail(to: order.user.email, subject: 'Order Confirmation')
  end
end
```

## Security Notes

When handling user input in services:
- Always use Rails strong parameters: `params.require(:order).permit(:allowed_fields)`
- Never pass raw `params[:order]` directly to model creation
- Whitelist only the specific attributes that should be mass-assignable

## Usage Guidelines

- Always use strong parameters to whitelist permitted attributes. Never allow mass assignment of sensitive fields like role, admin, etc.

