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
#  role       :string           default("user")
#  active     :boolean          default(true)
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: orders
#
#  id          :bigint           not null, primary key
#  user_id     :bigint           not null
#  total       :decimal(10,2)    not null
#  status      :string           default("pending")
#  order_date  :date             not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Table name: products
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  price       :decimal(8,2)     not null
#  category    :string           not null
#  sku         :string           not null
#  active      :boolean          default(true)
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :orders, dependent: :destroy
  
  validates :email, presence: true, uniqueness: true
  validates :name, presence: true
  
  enum role: { user: 'user', admin: 'admin', manager: 'manager' }
  
  scope :active, -> { where(active: true) }
  scope :by_role, ->(role) { where(role: role) }
  scope :recent, -> { where(created_at: 1.month.ago..) }
  
  def full_contact_info
    "#{name} <#{email}>"
  end
end

class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items
  
  validates :total, presence: true, numericality: { greater_than: 0 }
  validates :order_date, presence: true
  
  enum status: { pending: 'pending', confirmed: 'confirmed', shipped: 'shipped', delivered: 'delivered' }
  
  scope :completed, -> { where(status: ['shipped', 'delivered']) }
  scope :for_date_range, ->(start_date, end_date) { where(order_date: start_date..end_date) }
  scope :high_value, -> { where('total > ?', 100) }
  
  def self.total_revenue
    sum(:total)
  end
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :destroy
  has_many :orders, through: :order_items
  
  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
  validates :sku, presence: true, uniqueness: true
  
  scope :active, -> { where(active: true) }
  scope :by_category, ->(category) { where(category: category) }
  scope :price_range, ->(min, max) { where(price: min..max) }
  
  CATEGORIES = %w[electronics clothing books home sports].freeze
  
  def formatted_price
    "$#{price.to_f}"
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product
  
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }
end
```
