# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: webhook_events
#
#  id               :bigint           not null, primary key
#  external_id      :string           not null
#  event_type       :string           not null
#  payload          :json             not null
#  processed_at     :datetime
#  created_at       :datetime         not null
#  updated_at       :datetime         not null
#
# Indexes
#
#  index_webhook_events_on_external_id  (external_id) UNIQUE
#  index_webhook_events_on_event_type   (event_type)
#

# Table name: orders
#
#  id               :bigint           not null, primary key
#  external_id      :string           not null
#  status           :string           default("pending")
#  amount_cents     :integer          not null
#  customer_email   :string           not null
#  created_at       :datetime         not null
#  updated_at       :datetime         not null
#
# Indexes
#
#  index_orders_on_external_id  (external_id) UNIQUE
#

# Table name: payments
#
#  id               :bigint           not null, primary key
#  order_id         :bigint           not null
#  external_id      :string           not null
#  status           :string           default("pending")
#  amount_cents     :integer          not null
#  processed_at     :datetime
#  created_at       :datetime         not null
#  updated_at       :datetime         not null
#
# Indexes
#
#  index_payments_on_order_id      (order_id)
#  index_payments_on_external_id   (external_id) UNIQUE
#
```

## Models

```ruby
class WebhookEvent < ApplicationRecord
  validates :external_id, presence: true, uniqueness: true
  validates :event_type, presence: true
  validates :payload, presence: true

  scope :processed, -> { where.not(processed_at: nil) }
  scope :unprocessed, -> { where(processed_at: nil) }
  scope :by_type, ->(type) { where(event_type: type) }

  def processed?
    processed_at.present?
  end

  def mark_as_processed!
    update!(processed_at: Time.current)
  end
end

class Order < ApplicationRecord
  has_many :payments, dependent: :destroy

  validates :external_id, presence: true, uniqueness: true
  validates :status, inclusion: { in: %w[pending confirmed cancelled] }
  validates :amount_cents, presence: true, numericality: { greater_than: 0 }
  validates :customer_email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }

  scope :by_status, ->(status) { where(status: status) }

  def confirmed?
    status == 'confirmed'
  end

  def cancelled?
    status == 'cancelled'
  end
end

class Payment < ApplicationRecord
  belongs_to :order

  validates :external_id, presence: true, uniqueness: true
  validates :status, inclusion: { in: %w[pending completed failed] }
  validates :amount_cents, presence: true, numericality: { greater_than: 0 }

  scope :by_status, ->(status) { where(status: status) }
  scope :completed, -> { where(status: 'completed') }

  def completed?
    status == 'completed'
  end

  def failed?
    status == 'failed'
  end

  def complete!
    update!(status: 'completed', processed_at: Time.current)
  end
end

class WebhookProcessor
  SUPPORTED_EVENTS = %w[
    order.created
    order.updated
    payment.completed
    payment.failed
  ].freeze

  def self.supported_event?(event_type)
    SUPPORTED_EVENTS.include?(event_type)
  end

  private

  def process_order_created(payload)
    Order.create!(
      external_id: payload['id'],
      amount_cents: payload['amount_cents'],
      customer_email: payload['customer_email'],
      status: 'pending'
    )
  end

  def process_payment_completed(payload)
    payment = Payment.find_by!(external_id: payload['id'])
    payment.complete!
    payment.order.update!(status: 'confirmed')
  end
end
```
