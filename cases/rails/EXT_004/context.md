# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id                :bigint           not null, primary key
#  user_id           :bigint           not null
#  external_order_id :string
#  status            :string           default("pending"), not null
#  total_amount      :decimal(10,2)    not null
#  retry_count       :integer          default(0)
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#
# Indexes
#
#  index_orders_on_user_id                            (user_id)
#  index_orders_on_external_order_id                  (external_order_id)
#  index_orders_on_user_id_and_external_order_id      (user_id,external_order_id) UNIQUE
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
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :products, through: :order_items

  validates :status, inclusion: { in: %w[pending processing completed failed cancelled] }
  validates :total_amount, presence: true, numericality: { greater_than: 0 }
  validates :external_order_id, uniqueness: { scope: :user_id }, allow_nil: true

  scope :pending, -> { where(status: 'pending') }
  scope :failed, -> { where(status: 'failed') }
  scope :completed, -> { where(status: 'completed') }
  scope :for_user, ->(user) { where(user: user) }
  scope :with_external_id, ->(external_id) { where(external_order_id: external_id) }

  MAX_RETRY_ATTEMPTS = 3

  def can_retry?
    failed? && retry_count < MAX_RETRY_ATTEMPTS
  end

  def increment_retry_count!
    increment!(:retry_count)
  end

  def mark_as_failed!
    update!(status: 'failed')
  end

  def mark_as_completed!
    update!(status: 'completed')
  end

  def duplicate_for_user?
    return false unless external_order_id.present?
    
    self.class.for_user(user)
              .with_external_id(external_order_id)
              .where.not(id: id)
              .exists?
  end

  private

  def failed?
    status == 'failed'
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }
end

class User < ApplicationRecord
  has_many :orders, dependent: :destroy

  def recent_orders(limit = 10)
    orders.order(created_at: :desc).limit(limit)
  end
end

class Product < ApplicationRecord
  has_many :order_items
  has_many :orders, through: :order_items

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }

  scope :available, -> { where(available: true) }
end
```

## Usage Guidelines

- Implement idempotency for operations that may be retried. Network errors can cause duplicate requests even when the first succeeded.

