# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: deliveries
#
#  id                :bigint           not null, primary key
#  tracking_number   :string           not null
#  status           :integer          default("pending"), not null
#  shipped_at       :datetime
#  delivered_at     :datetime
#  created_at       :datetime         not null
#  updated_at       :datetime         not null
#  order_id         :bigint           not null
#
# Indexes
#
#  index_deliveries_on_order_id         (order_id)
#  index_deliveries_on_tracking_number  (tracking_number) UNIQUE
#  index_deliveries_on_status          (status)
#

# Table name: delivery_status_transitions
#
#  id           :bigint           not null, primary key
#  delivery_id  :bigint           not null
#  from_status  :string
#  to_status    :string           not null
#  transitioned_at :datetime      not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Indexes
#
#  index_delivery_status_transitions_on_delivery_id  (delivery_id)
#
```

## Models

```ruby
class Delivery < ApplicationRecord
  belongs_to :order
  has_many :status_transitions, class_name: 'DeliveryStatusTransition', dependent: :destroy

  validates :tracking_number, presence: true, uniqueness: true
  validates :status, presence: true

  enum status: {
    pending: 0,
    processing: 1,
    shipped: 2,
    out_for_delivery: 3,
    delivered: 4,
    failed: 5,
    returned: 6
  }

  scope :active, -> { where.not(status: [:delivered, :failed, :returned]) }
  scope :completed, -> { where(status: [:delivered, :failed, :returned]) }

  STATUS_PROGRESSION = {
    'pending' => ['processing', 'failed'],
    'processing' => ['shipped', 'failed'],
    'shipped' => ['out_for_delivery', 'failed', 'returned'],
    'out_for_delivery' => ['delivered', 'failed', 'returned'],
    'delivered' => [],
    'failed' => [],
    'returned' => []
  }.freeze

  def can_transition_to?(new_status)
    STATUS_PROGRESSION[status]&.include?(new_status.to_s)
  end

  def terminal_status?
    %w[delivered failed returned].include?(status)
  end

  private

  def record_status_transition(from_status, to_status)
    status_transitions.create!(
      from_status: from_status,
      to_status: to_status,
      transitioned_at: Time.current
    )
  end

  def update_timestamps_for_status
    case status
    when 'shipped'
      update_column(:shipped_at, Time.current) if shipped_at.nil?
    when 'delivered'
      update_column(:delivered_at, Time.current) if delivered_at.nil?
    end
  end
end

class DeliveryStatusTransition < ApplicationRecord
  belongs_to :delivery

  validates :to_status, presence: true
  validates :transitioned_at, presence: true

  scope :recent, -> { order(transitioned_at: :desc) }
  scope :for_status, ->(status) { where(to_status: status) }
end

class Order < ApplicationRecord
  has_many :deliveries, dependent: :destroy

  def primary_delivery
    deliveries.first
  end
end
```