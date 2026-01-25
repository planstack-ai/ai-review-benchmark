# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: products
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  price       :decimal(10,2)    not null
#  active      :boolean          default(true), not null
#  featured    :boolean          default(false), not null
#  category_id :bigint
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes:
#   index_products_on_active   (active)
#   index_products_on_featured (featured)
```

## Models

```ruby
class Product < ApplicationRecord
  belongs_to :category, optional: true

  # Default scope ensures customer-facing queries only show active products
  default_scope { where(active: true) }

  scope :featured, -> { where(featured: true) }
  scope :in_category, ->(category_id) { where(category_id: category_id) }
  scope :recently_updated, -> { order(updated_at: :desc) }

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
end

class Category < ApplicationRecord
  has_many :products
end
```

## Usage Guidelines

- Use `unscoped` to bypass default_scope when needed for admin operations
- Be aware that default_scope affects all queries on the model including associations
