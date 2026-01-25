# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: products
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  description :text
#  price       :decimal(10,2)    not null
#  sku         :string           not null
#  category_id :bigint
#  active      :boolean          default(true)
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  user_id      :bigint           not null
#  total_amount :decimal(10,2)    not null
#  status       :string           default("pending")
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  unit_price :decimal(10,2)    not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class Product < ApplicationRecord
  belongs_to :category
  has_many :order_items, dependent: :restrict_with_error
  
  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
  validates :sku, presence: true, uniqueness: true
  
  scope :active, -> { where(active: true) }
  scope :by_category, ->(category) { where(category: category) }
  
  def display_name
    "#{name} (#{sku})"
  end
  
  def formatted_price
    "$#{price.to_f}"
  end
end

class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items
  
  validates :total_amount, presence: true, numericality: { greater_than: 0 }
  validates :status, inclusion: { in: %w[pending confirmed shipped delivered cancelled] }
  
  scope :recent, -> { order(created_at: :desc) }
  scope :by_status, ->(status) { where(status: status) }
  
  def calculate_total
    order_items.sum { |item| item.quantity * item.unit_price }
  end
  
  def item_count
    order_items.sum(:quantity)
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
  
  def product_name_at_time
    product.name
  end
end

class User < ApplicationRecord
  has_many :orders, dependent: :destroy
  
  validates :email, presence: true, uniqueness: true
end

class Category < ApplicationRecord
  has_many :products, dependent: :destroy
  
  validates :name, presence: true
end
```
