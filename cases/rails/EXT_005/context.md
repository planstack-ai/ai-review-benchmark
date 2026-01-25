# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: warehouses
#
#  id                    :bigint           not null, primary key
#  name                  :string           not null
#  sync_delay_minutes    :integer          default(15), not null
#  last_synced_at        :datetime
#  active                :boolean          default(true), not null
#  created_at            :datetime         not null
#  updated_at            :datetime         not null
#

# == Schema Information
#
# Table name: inventory_items
#
#  id                    :bigint           not null, primary key
#  warehouse_id          :bigint           not null
#  sku                   :string           not null
#  quantity              :integer          default(0), not null
#  reserved_quantity     :integer          default(0), not null
#  last_updated_at       :datetime         not null
#  created_at            :datetime         not null
#  updated_at            :datetime         not null
#
```

## Models

```ruby
class Warehouse < ApplicationRecord
  has_many :inventory_items, dependent: :destroy
  
  validates :name, presence: true
  validates :sync_delay_minutes, presence: true, numericality: { greater_than: 0 }
  
  scope :active, -> { where(active: true) }
  scope :recently_synced, -> { where('last_synced_at > ?', 1.hour.ago) }
  
  def sync_threshold_time
    sync_delay_minutes.minutes.ago
  end
  
  def sync_overdue?
    last_synced_at.nil? || last_synced_at < sync_threshold_time
  end
end

class InventoryItem < ApplicationRecord
  belongs_to :warehouse
  
  validates :sku, presence: true, uniqueness: { scope: :warehouse_id }
  validates :quantity, :reserved_quantity, presence: true, numericality: { greater_than_or_equal_to: 0 }
  validates :last_updated_at, presence: true
  
  scope :available, -> { where('quantity > reserved_quantity') }
  scope :out_of_stock, -> { where(quantity: 0) }
  scope :recently_updated, ->(time) { where('last_updated_at > ?', time) }
  
  def available_quantity
    [quantity - reserved_quantity, 0].max
  end
  
  def stale_data?
    last_updated_at < warehouse.sync_threshold_time
  end
end

class InventoryService
  class << self
    def check_availability(sku, requested_quantity, warehouse_ids = nil)
      scope = InventoryItem.joins(:warehouse)
                          .where(warehouses: { active: true })
                          .where(sku: sku)
      
      scope = scope.where(warehouse_id: warehouse_ids) if warehouse_ids.present?
      
      scope.available.sum(:quantity) >= requested_quantity
    end
    
    def find_sufficient_stock(sku, requested_quantity)
      InventoryItem.joins(:warehouse)
                   .where(warehouses: { active: true })
                   .where(sku: sku)
                   .available
                   .where('quantity - reserved_quantity >= ?', requested_quantity)
                   .first
    end
  end
end
```

## Usage Guidelines

- Account for synchronization delays with external systems. Data may not be immediately consistent across services.

