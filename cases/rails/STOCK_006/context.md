# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: products
#
#  id                     :bigint           not null, primary key
#  name                   :string           not null
#  sku                    :string           not null
#  stock_quantity         :integer          default(0), not null
#  reserved_quantity      :integer          default(0), not null
#  negative_stock_allowed :boolean          default(false), not null
#  created_at            :datetime         not null
#  updated_at            :datetime         not null
#
# Indexes
#
#  index_products_on_sku  (sku) UNIQUE
#

# Table name: inventory_transactions
#
#  id         :bigint           not null, primary key
#  product_id :bigint           not null
#  quantity   :integer          not null
#  reason     :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_inventory_transactions_on_product_id  (product_id)
#
# Foreign Keys
#
#  fk_rails_...  (product_id => products.id)
```

## Models

```ruby
class Product < ApplicationRecord
  has_many :inventory_transactions, dependent: :destroy

  validates :name, presence: true
  validates :sku, presence: true, uniqueness: true
  validates :stock_quantity, :reserved_quantity, numericality: { greater_than_or_equal_to: 0 }

  scope :in_stock, -> { where('stock_quantity > reserved_quantity') }
  scope :out_of_stock, -> { where('stock_quantity <= reserved_quantity') }
  scope :low_stock, ->(threshold = 10) { where('stock_quantity - reserved_quantity <= ?', threshold) }

  def available_quantity
    stock_quantity - reserved_quantity
  end

  def in_stock?
    available_quantity > 0
  end

  def can_fulfill?(requested_quantity)
    available_quantity >= requested_quantity
  end

  def reserve_stock(quantity)
    return false unless can_fulfill?(quantity)
    
    increment!(:reserved_quantity, quantity)
    true
  end

  def release_reserved_stock(quantity)
    new_reserved = [reserved_quantity - quantity, 0].max
    update!(reserved_quantity: new_reserved)
  end

  private

  def log_inventory_change(quantity, reason)
    inventory_transactions.create!(
      quantity: quantity,
      reason: reason
    )
  end
end

class InventoryTransaction < ApplicationRecord
  belongs_to :product

  validates :quantity, presence: true, numericality: { other_than: 0 }
  validates :reason, presence: true

  REASONS = %w[
    purchase
    sale
    adjustment
    damage
    return
    transfer
  ].freeze

  validates :reason, inclusion: { in: REASONS }

  scope :increases, -> { where('quantity > 0') }
  scope :decreases, -> { where('quantity < 0') }
  scope :recent, -> { order(created_at: :desc) }
end

class InventoryService
  class InsufficientStockError < StandardError
    attr_reader :product, :requested_quantity, :available_quantity

    def initialize(product, requested_quantity, available_quantity)
      @product = product
      @requested_quantity = requested_quantity
      @available_quantity = available_quantity
      super("Insufficient stock for #{product.sku}: requested #{requested_quantity}, available #{available_quantity}")
    end
  end

  def self.adjust_stock(product, quantity, reason)
    new(product).adjust_stock(quantity, reason)
  end

  def initialize(product)
    @product = product
  end

  private

  attr_reader :product
end
```