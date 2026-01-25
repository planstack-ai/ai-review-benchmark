# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: products
#
#  id          :bigint           not null, primary key
#  name        :string           not null
#  sku         :string           not null
#  price       :decimal(10,2)    not null
#  category_id :bigint           not null
#  active      :boolean          default(true)
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_products_on_category_id  (category_id)
#  index_products_on_sku          (sku) UNIQUE
#

# Table name: categories
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  slug       :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_categories_on_slug  (slug) UNIQUE
#

# Table name: inventory_items
#
#  id         :bigint           not null, primary key
#  product_id :bigint           not null
#  quantity   :integer          default(0)
#  location   :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_inventory_items_on_product_id_and_location  (product_id,location) UNIQUE
#
```

## Models

```ruby
class Product < ApplicationRecord
  belongs_to :category
  has_many :inventory_items, dependent: :destroy

  validates :name, presence: true
  validates :sku, presence: true, uniqueness: true
  validates :price, presence: true, numericality: { greater_than: 0 }

  scope :active, -> { where(active: true) }
  scope :by_category, ->(category) { where(category: category) }

  BATCH_SIZE = 1000
  MAX_BULK_INSERT_SIZE = 5000

  def self.find_existing_skus(skus)
    where(sku: skus).pluck(:sku).to_set
  end

  def self.validate_bulk_data(products_data)
    errors = []
    skus = products_data.map { |p| p[:sku] }
    
    if skus.length != skus.uniq.length
      errors << "Duplicate SKUs found in batch"
    end

    existing_skus = find_existing_skus(skus)
    duplicate_skus = skus.select { |sku| existing_skus.include?(sku) }
    
    if duplicate_skus.any?
      errors << "SKUs already exist: #{duplicate_skus.join(', ')}"
    end

    errors
  end
end

class Category < ApplicationRecord
  has_many :products, dependent: :destroy

  validates :name, presence: true
  validates :slug, presence: true, uniqueness: true

  def self.find_by_name_or_slug(identifier)
    find_by(name: identifier) || find_by(slug: identifier)
  end

  def self.id_mapping
    pluck(:name, :id).to_h
  end
end

class InventoryItem < ApplicationRecord
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than_or_equal_to: 0 }
  validates :location, presence: true
  validates :product_id, uniqueness: { scope: :location }

  scope :by_location, ->(location) { where(location: location) }
  scope :with_stock, -> { where('quantity > 0') }

  WAREHOUSE_LOCATIONS = %w[A1 A2 B1 B2 C1 C2].freeze
  DEFAULT_LOCATION = 'A1'.freeze
end
```