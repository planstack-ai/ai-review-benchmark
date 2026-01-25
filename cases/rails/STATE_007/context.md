# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id              :bigint           not null, primary key
#  user_id         :bigint           not null
#  status          :string           not null
#  delivery_status :string           default("pending"), not null
#  shipped_at      :datetime
#  delivered_at    :datetime
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
#
# Indexes
#
#  index_orders_on_user_id          (user_id)
#  index_orders_on_delivery_status  (delivery_status)
#
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user

  DELIVERY_STATUSES = %w[pending processing shipped delivered cancelled].freeze

  validates :status, presence: true
  validates :delivery_status, inclusion: { in: DELIVERY_STATUSES }

  scope :pending_delivery, -> { where(delivery_status: 'pending') }
  scope :shipped, -> { where(delivery_status: 'shipped') }
  scope :delivered, -> { where(delivery_status: 'delivered') }

  # Status progression rules (forward only)
  DELIVERY_PROGRESSION = {
    'pending' => %w[processing cancelled],
    'processing' => %w[shipped cancelled],
    'shipped' => %w[delivered],
    'delivered' => [],
    'cancelled' => []
  }.freeze

  def can_transition_to?(new_status)
    DELIVERY_PROGRESSION[delivery_status]&.include?(new_status.to_s)
  end

  def terminal_delivery_status?
    %w[delivered cancelled].include?(delivery_status)
  end
end
```

## Jobs

```ruby
class DeliveryNotificationJob < ApplicationJob
  queue_as :notifications

  def perform(order_id, new_status)
    order = Order.find(order_id)
    # Send notification based on status
    case new_status.to_sym
    when :shipped
      OrderMailer.shipped(order).deliver_now
    when :delivered
      OrderMailer.delivered(order).deliver_now
    when :cancelled
      OrderMailer.cancelled(order).deliver_now
    end
  end
end
```

## State Machine Business Rules

Delivery status transitions must follow these rules:
1. **Forward-only progression**: Statuses can only move forward in the workflow (pending → processing → shipped → delivered)
2. **Terminal states**: Once "delivered" or "cancelled", no further transitions are allowed
3. **Cancellation exception**: "cancelled" can be reached from "pending" or "processing" only
4. **No backward transitions**: A delivered package cannot return to "shipped" or earlier states
5. **Status regression prevention**: The system must explicitly prevent transitions to earlier states in the workflow
