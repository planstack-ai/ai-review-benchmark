# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: payments
#
#  id                :bigint           not null, primary key
#  amount_cents      :integer          not null
#  currency          :string           not null, default("USD")
#  status            :string           not null, default("pending")
#  external_id       :string
#  gateway_response  :text
#  processed_at      :datetime
#  failed_at         :datetime
#  retry_count       :integer          default(0)
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#  order_id          :bigint           not null
#
# Table name: orders
#
#  id                :bigint           not null, primary key
#  user_id           :bigint           not null
#  total_cents       :integer          not null
#  status            :string           not null, default("pending")
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
```

## Models

```ruby
class Payment < ApplicationRecord
  STATUSES = %w[pending processing completed failed timeout].freeze
  MAX_RETRIES = 3
  TIMEOUT_DURATION = 30.seconds

  belongs_to :order

  validates :amount_cents, presence: true, numericality: { greater_than: 0 }
  validates :currency, presence: true
  validates :status, inclusion: { in: STATUSES }

  scope :pending, -> { where(status: 'pending') }
  scope :processing, -> { where(status: 'processing') }
  scope :completed, -> { where(status: 'completed') }
  scope :failed, -> { where(status: 'failed') }
  scope :timed_out, -> { where(status: 'timeout') }
  scope :retryable, -> { where('retry_count < ?', MAX_RETRIES) }

  def amount
    Money.new(amount_cents, currency)
  end

  def can_retry?
    retry_count < MAX_RETRIES && %w[failed timeout].include?(status)
  end

  def mark_as_processing!
    update!(status: 'processing', processed_at: Time.current)
  end

  def mark_as_completed!(external_id, response = nil)
    update!(
      status: 'completed',
      external_id: external_id,
      gateway_response: response,
      processed_at: Time.current
    )
  end

  def mark_as_failed!(response = nil)
    update!(
      status: 'failed',
      gateway_response: response,
      failed_at: Time.current,
      retry_count: retry_count + 1
    )
  end

  def mark_as_timeout!
    update!(
      status: 'timeout',
      failed_at: Time.current,
      retry_count: retry_count + 1
    )
  end
end

class Order < ApplicationRecord
  STATUSES = %w[pending paid cancelled].freeze

  belongs_to :user
  has_many :payments, dependent: :destroy

  validates :total_cents, presence: true, numericality: { greater_than: 0 }
  validates :status, inclusion: { in: STATUSES }

  def total
    Money.new(total_cents, 'USD')
  end

  def mark_as_paid!
    update!(status: 'paid')
  end
end

class PaymentGateway
  class TimeoutError < StandardError; end
  class ProcessingError < StandardError; end

  def self.process_payment(payment)
    new.process_payment(payment)
  end

  def process_payment(payment)
    response = gateway_client.charge(
      amount: payment.amount_cents,
      currency: payment.currency
    )
    
    { success: true, transaction_id: response.id, response: response }
  rescue Net::TimeoutError, Timeout::Error => e
    raise TimeoutError, "Payment gateway timeout: #{e.message}"
  rescue StandardError => e
    raise ProcessingError, "Payment processing failed: #{e.message}"
  end

  private

  def gateway_client
    @gateway_client ||= StripeClient.new
  end
end
```

## Usage Guidelines

- Always handle timeouts when calling external APIs. Consider what state the system should be in when we don't know if the external call succeeded. Implement monitoring and manual recovery procedures.

