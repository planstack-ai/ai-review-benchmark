# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id            :bigint           not null, primary key
#  user_id       :bigint           not null
#  status        :string           not null
#  total_amount  :decimal(10, 2)   not null
#  shipped_at    :datetime
#  created_at    :datetime         not null
#  updated_at    :datetime         not null
#
# Indexes
#
#  index_orders_on_user_id        (user_id)
#  index_orders_on_status         (status)
#  index_orders_on_created_at     (created_at)
#

# Table name: items (order line items)
#
#  id            :bigint           not null, primary key
#  order_id      :bigint           not null
#  product_name  :string           not null
#  quantity      :integer          not null
#  price         :decimal(10, 2)   not null
#  fulfilled     :boolean          default(false)
#  created_at    :datetime         not null
#  updated_at    :datetime         not null
#
# Indexes
#
#  index_items_on_order_id   (order_id)
#

# Table name: payments
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  amount     :decimal(10, 2)   not null
#  status     :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#

# Table name: shipping_addresses
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  street     :string           not null
#  city       :string           not null
#  state      :string           not null
#  zip        :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
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
end

class Order < ApplicationRecord
  belongs_to :user
  has_many :items, dependent: :destroy
  has_many :payments, dependent: :destroy
  has_one :shipping_address, dependent: :destroy

  validates :status, presence: true, inclusion: { in: %w[pending confirmed shipped delivered completed cancelled] }
  validates :total_amount, presence: true, numericality: { greater_than: 0 }

  scope :pending, -> { where(status: 'pending') }
  scope :completed, -> { where(status: 'completed') }
  scope :shipped, -> { where(status: 'shipped') }
end

class Item < ApplicationRecord
  belongs_to :order

  validates :product_name, presence: true
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }

  def fulfilled?
    fulfilled
  end
end

class Payment < ApplicationRecord
  belongs_to :order

  validates :amount, presence: true, numericality: { greater_than: 0 }
  validates :status, presence: true
end

class ShippingAddress < ApplicationRecord
  belongs_to :order

  validates :street, :city, :state, :zip, presence: true
end
```

## Performance Guidelines

When counting associations in Rails:
- Use `.count` for efficient SQL COUNT queries
- Use `.length` only when records are already loaded
- Use `.size` which automatically chooses the best approach
- Avoid loading full association collections just to count them
