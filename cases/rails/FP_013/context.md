# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  user_id      :bigint           not null
#  status       :string           not null
#  total_amount :decimal(10,2)    not null
#  shipped_at   :datetime
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Indexes
#
#  index_orders_on_user_id  (user_id)
#  index_orders_on_status   (status)
#

# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  price      :decimal(8,2)     not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_order_items_on_order_id    (order_id)
#  index_order_items_on_product_id  (product_id)
#

# Table name: inventory_items
#
#  id           :bigint           not null, primary key
#  product_id   :bigint           not null
#  warehouse_id :bigint           not null
#  quantity     :integer          not null, default: 0
#  reserved     :integer          not null, default: 0
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Indexes
#
#  index_inventory_items_on_product_id_and_warehouse_id  (product_id,warehouse_id) UNIQUE
#
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  STATUSES = %w[pending confirmed processing shipped delivered cancelled].freeze

  validates :status, inclusion: { in: STATUSES }
  validates :total_amount, presence: true, numericality: { greater_than: 0 }

  scope :pending, -> { where(status: 'pending') }
  scope :confirmed, -> { where(status: 'confirmed') }
  scope :processing, -> { where(status: 'processing') }
  scope :shipped, -> { where(status: 'shipped') }
  scope :older_than, ->(date) { where('created_at < ?', date) }

  after_update :send_status_notification, if: :saved_change_to_status?
  after_update :update_shipped_timestamp, if: -> { status == 'shipped' && saved_change_to_status? }

  private

  def send_status_notification
    OrderStatusMailer.status_changed(self).deliver_later
  end

  def update_shipped_timestamp
    update_column(:shipped_at, Time.current)
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }

  scope :for_product, ->(product_id) { where(product_id: product_id) }
end

class InventoryItem < ApplicationRecord
  belongs_to :product
  belongs_to :warehouse

  validates :quantity, presence: true, numericality: { greater_than_or_equal_to: 0 }
  validates :reserved, presence: true, numericality: { greater_than_or_equal_to: 0 }

  scope :for_product, ->(product_id) { where(product_id: product_id) }
  scope :with_available_stock, -> { where('quantity > reserved') }

  def available_quantity
    quantity - reserved
  end
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :destroy
  has_many :inventory_items, dependent: :destroy
  has_many :orders, through: :order_items

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }

  scope :active, -> { where(active: true) }
end
```