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
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#  processed_at :datetime
#
# Indexes
#
#  index_orders_on_user_id                    (user_id)
#  index_orders_on_status                     (status)
#  index_orders_on_created_at                 (created_at)
#  index_orders_on_status_and_created_at      (status,created_at)
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
```

## Models

```ruby
class Order < ApplicationRecord
  BATCH_SIZE = 1000
  PROCESSING_TIMEOUT = 30.minutes

  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  validates :status, inclusion: { in: %w[pending processing completed failed] }
  validates :total_amount, presence: true, numericality: { greater_than: 0 }

  scope :pending, -> { where(status: 'pending') }
  scope :processing, -> { where(status: 'processing') }
  scope :completed, -> { where(status: 'completed') }
  scope :failed, -> { where(status: 'failed') }
  scope :created_before, ->(time) { where('created_at < ?', time) }
  scope :created_after, ->(time) { where('created_at > ?', time) }
  scope :by_status_and_date, ->(status, date) { where(status: status, created_at: date.beginning_of_day..date.end_of_day) }

  def mark_as_processing!
    update!(status: 'processing', processed_at: Time.current)
  end

  def mark_as_completed!
    update!(status: 'completed')
  end

  def mark_as_failed!
    update!(status: 'failed')
  end

  def processing_expired?
    processing? && processed_at && processed_at < PROCESSING_TIMEOUT.ago
  end

  def total_items
    order_items.sum(:quantity)
  end

  private

  def calculate_total
    order_items.sum { |item| item.quantity * item.price }
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }

  scope :by_product, ->(product_id) { where(product_id: product_id) }
end

class Product < ApplicationRecord
  has_many :order_items, dependent: :destroy
  has_many :orders, through: :order_items

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }

  scope :active, -> { where(active: true) }
end

class OrderProcessingService
  def initialize
    @processed_count = 0
    @failed_count = 0
  end

  private

  attr_reader :processed_count, :failed_count

  def process_single_order(order)
    return false unless order.pending?

    order.mark_as_processing!
    
    # Simulate processing logic
    if perform_order_processing(order)
      order.mark_as_completed!
      @processed_count += 1
      true
    else
      order.mark_as_failed!
      @failed_count += 1
      false
    end
  rescue StandardError => e
    Rails.logger.error "Failed to process order #{order.id}: #{e.message}"
    order.mark_as_failed!
    @failed_count += 1
    false
  end

  def perform_order_processing(order)
    # Simulate external API call or complex business logic
    sleep(0.1)
    order.total_amount > 0
  end

  def log_processing_summary
    Rails.logger.info "Order processing completed: #{processed_count} processed, #{failed_count} failed"
  end
end
```

## Usage Guidelines

- Never load entire tables into memory. Use `find_each` or `find_in_batches` for batch processing large datasets.

