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
#  member     :boolean          default(false), not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#

# == Schema Information
#
# Table name: products
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  price_cents :integer          not null
#  active      :boolean          default(true), not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#

# == Schema Information
#
# Table name: orders
#
#  id               :bigint           not null, primary key
#  user_id          :bigint           not null
#  total_cents      :integer          not null
#  discount_cents   :integer          default(0), not null
#  status           :string           default("pending"), not null
#  created_at       :datetime         not null
#  updated_at       :datetime         not null
#
```

## Models

```ruby
class User < ApplicationRecord
  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true

  scope :members, -> { where(member: true) }
  scope :non_members, -> { where(member: false) }

  def member?
    member
  end
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :destroy
  has_many :orders, through: :order_items

  validates :name, presence: true
  validates :price_cents, presence: true, numericality: { greater_than: 0 }

  scope :active, -> { where(active: true) }

  def price
    Money.new(price_cents)
  end
end

class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  validates :total_cents, presence: true, numericality: { greater_than: 0 }
  validates :discount_cents, numericality: { greater_than_or_equal_to: 0 }
  validates :status, inclusion: { in: %w[pending confirmed shipped delivered cancelled] }

  scope :confirmed, -> { where(status: 'confirmed') }
  scope :with_discount, -> { where('discount_cents > 0') }

  def subtotal
    Money.new(order_items.sum { |item| item.quantity * item.unit_price_cents })
  end

  def total
    Money.new(total_cents)
  end

  def discount
    Money.new(discount_cents)
  end

  def final_amount
    subtotal - discount
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :unit_price_cents, presence: true, numericality: { greater_than: 0 }

  def line_total
    Money.new(quantity * unit_price_cents)
  end
end
```