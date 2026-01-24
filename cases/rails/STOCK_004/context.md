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
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_products_on_sku  (sku) UNIQUE
#

# == Schema Information
#
# Table name: inventory_items
#
#  id               :bigint           not null, primary key
#  product_id       :bigint           not null
#  warehouse_id     :bigint           not null
#  quantity_on_hand :integer          default(0), not null
#  reserved_quantity :integer         default(0), not null
#  created_at       :datetime         not null
#  updated_at       :datetime         not null
#
# Indexes
#
#  index_inventory_items_on_product_id    (product_id)
#  index_inventory_items_on_warehouse_id  (warehouse_id)
#  index_inventory_items_unique           (product_id,warehouse_id) UNIQUE
#

# == Schema Information
#
# Table name: reservations
#
#  id               :bigint           not null, primary key
#  inventory_item_id :bigint          not null
#  order_id         :bigint           not null
#  quantity         :integer          not null
#  status           :string           default("active"), not null
#  expires_at       :datetime
#  created_at       :datetime         not null
#  updated_at       :datetime         not null
#
# Indexes
#
#  index_reservations_on_inventory_item_id  (inventory_item_id)
#  index_reservations_on_order_id           (order_id)
#  index_reservations_on_status             (status)
#
```

## Models

```ruby
class Product < ApplicationRecord
  has_many :inventory_items, dependent: :destroy
  
  validates :name, presence: true
  validates :sku, presence: true, uniqueness: true
  
  def total_quantity_on_hand
    inventory_items.sum(:quantity_on_hand)
  end
  
  def total_reserved_quantity
    inventory_items.sum(:reserved_quantity)
  end
end

class InventoryItem < ApplicationRecord
  belongs_to :product
  belongs_to :warehouse
  has_many :reservations, dependent: :destroy
  
  validates :quantity_on_hand, presence: true, numericality: { greater_than_or_equal_to: 0 }
  validates :reserved_quantity, presence: true, numericality: { greater_than_or_equal_to: 0 }
  validates :product_id, uniqueness: { scope: :warehouse_id }
  
  scope :with_stock, -> { where('quantity_on_hand > 0') }
  scope :low_stock, ->(threshold = 10) { where('quantity_on_hand <= ?', threshold) }
  
  def available_quantity
    quantity_on_hand - reserved_quantity
  end
  
  def can_reserve?(quantity)
    available_quantity >= quantity
  end
end

class Reservation < ApplicationRecord
  belongs_to :inventory_item
  belongs_to :order
  
  STATUSES = %w[active fulfilled cancelled expired].freeze
  
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :status, inclusion: { in: STATUSES }
  
  scope :active, -> { where(status: 'active') }
  scope :expired, -> { where('expires_at < ?', Time.current) }
  scope :expiring_soon, ->(hours = 24) { where('expires_at < ?', hours.hours.from_now) }
  
  before_create :set_expiration
  after_create :increment_reserved_quantity
  after_update :update_reserved_quantity, if: :saved_change_to_status?
  
  private
  
  def set_expiration
    self.expires_at ||= 2.hours.from_now
  end
  
  def increment_reserved_quantity
    inventory_item.increment!(:reserved_quantity, quantity) if active?
  end
  
  def update_reserved_quantity
    return unless status_previously_was == 'active'
    inventory_item.decrement!(:reserved_quantity, quantity)
  end
end

class Warehouse < ApplicationRecord
  has_many :inventory_items, dependent: :destroy
  
  validates :name, presence: true
  validates :code, presence: true, uniqueness: true
end
```