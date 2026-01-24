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
#  product_type :string          not null
#  stock_count :integer          default(0)
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Table name: bundle_components
#
#  id          :bigint           not null, primary key
#  bundle_id   :bigint           not null
#  component_id :bigint          not null
#  quantity    :integer          not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Table name: inventory_movements
#
#  id          :bigint           not null, primary key
#  product_id  :bigint           not null
#  movement_type :string         not null
#  quantity    :integer          not null
#  created_at  :datetime         not null
#
```

## Models

```ruby
class Product < ApplicationRecord
  PRODUCT_TYPES = %w[simple bundle].freeze
  
  has_many :bundle_components, foreign_key: :bundle_id, dependent: :destroy
  has_many :components, through: :bundle_components, source: :component
  has_many :component_bundles, class_name: 'BundleComponent', foreign_key: :component_id
  has_many :bundles, through: :component_bundles, source: :bundle
  has_many :inventory_movements, dependent: :destroy
  
  validates :name, presence: true
  validates :sku, presence: true, uniqueness: true
  validates :product_type, inclusion: { in: PRODUCT_TYPES }
  validates :stock_count, numericality: { greater_than_or_equal_to: 0 }
  
  scope :bundles, -> { where(product_type: 'bundle') }
  scope :simple_products, -> { where(product_type: 'simple') }
  scope :in_stock, -> { where('stock_count > 0') }
  
  def bundle?
    product_type == 'bundle'
  end
  
  def simple?
    product_type == 'simple'
  end
  
  def component_quantities
    bundle_components.includes(:component).pluck(:component_id, :quantity).to_h
  end
end

class BundleComponent < ApplicationRecord
  belongs_to :bundle, class_name: 'Product'
  belongs_to :component, class_name: 'Product'
  
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :bundle_id, uniqueness: { scope: :component_id }
  
  scope :for_bundle, ->(bundle_id) { where(bundle_id: bundle_id) }
  scope :with_components, -> { includes(:component) }
end

class InventoryMovement < ApplicationRecord
  MOVEMENT_TYPES = %w[in out adjustment].freeze
  
  belongs_to :product
  
  validates :movement_type, inclusion: { in: MOVEMENT_TYPES }
  validates :quantity, presence: true, numericality: { other_than: 0 }
  
  scope :recent, -> { order(created_at: :desc) }
  scope :for_product, ->(product_id) { where(product_id: product_id) }
end
```