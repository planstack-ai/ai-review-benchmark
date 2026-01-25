# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: products
#
#  id             :bigint           not null, primary key
#  name           :string           not null
#  price          :decimal(10, 2)   not null
#  status         :string           default("active"), not null
#  stock_quantity :integer          default(0), not null
#  category_id    :bigint           not null
#  created_at     :datetime         not null
#  updated_at     :datetime         not null
#
# Indexes
#
#  index_products_on_category_id  (category_id)
#  index_products_on_status       (status)
#
# Table name: categories
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  price      :decimal(10, 2)   not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: product_views
#
#  id         :bigint           not null, primary key
#  product_id :bigint           not null
#  user_id    :bigint
#  created_at :datetime         not null
#
# Table name: reviews
#
#  id         :bigint           not null, primary key
#  product_id :bigint           not null
#  user_id    :bigint           not null
#  rating     :integer          not null
#  content    :text
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class Product < ApplicationRecord
  STATUSES = %w[active inactive discontinued].freeze

  belongs_to :category
  has_many :order_items, dependent: :restrict_with_error
  has_many :product_views, dependent: :destroy
  has_many :reviews, dependent: :destroy

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
  validates :status, inclusion: { in: STATUSES }
  validates :stock_quantity, numericality: { greater_than_or_equal_to: 0 }

  # Scope for filtering active products - should be used throughout the application
  scope :active, -> { where(status: 'active') }
  scope :in_stock, -> { where('stock_quantity > 0') }
  scope :by_category, ->(category) { where(category: category) }

  def average_rating
    reviews.average(:rating)&.round(2) || 0
  end
end

class Category < ApplicationRecord
  has_many :products, dependent: :restrict_with_error

  validates :name, presence: true, uniqueness: true
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }
end

class ProductView < ApplicationRecord
  belongs_to :product
  belongs_to :user, optional: true
end

class Review < ApplicationRecord
  belongs_to :product
  belongs_to :user

  validates :rating, presence: true, inclusion: { in: 1..5 }
end
```

## Usage Guidelines

The `Product.active` scope is the **canonical way** to filter active products throughout the application. This ensures:
- Consistent behavior when the definition of "active" changes
- DRY principle compliance
- Better maintainability

All queries for active products should use `Product.active` rather than `Product.where(status: 'active')`.
