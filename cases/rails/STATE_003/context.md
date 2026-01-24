# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id                :bigint           not null, primary key
#  user_id           :bigint           not null
#  status            :string           not null, default: "pending"
#  total_amount      :decimal(10,2)    not null
#  expires_at        :datetime
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#
# Table name: payments
#
#  id                :bigint           not null, primary key
#  order_id          :bigint           not null
#  amount            :decimal(10,2)    not null
#  status            :string           not null, default: "pending"
#  payment_method    :string           not null
#  processed_at      :datetime
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :payments, dependent: :destroy

  VALID_STATUSES = %w[pending confirmed cancelled expired].freeze
  EXPIRATION_WINDOW = 30.minutes

  validates :status, inclusion: { in: VALID_STATUSES }
  validates :total_amount, presence: true, numericality: { greater_than: 0 }

  scope :pending, -> { where(status: 'pending') }
  scope :expired, -> { where(status: 'expired') }
  scope :active, -> { where(status: %w[pending confirmed]) }
  scope :past_expiration, -> { where('expires_at < ?', Time.current) }

  before_create :set_expiration_time

  def expired?
    expires_at.present? && expires_at < Time.current
  end

  def can_accept_payment?
    pending? && !expired?
  end

  def mark_as_expired!
    update!(status: 'expired')
  end

  private

  def set_expiration_time
    self.expires_at = EXPIRATION_WINDOW.from_now
  end
end

class Payment < ApplicationRecord
  belongs_to :order

  VALID_STATUSES = %w[pending processing completed failed rejected].freeze

  validates :status, inclusion: { in: VALID_STATUSES }
  validates :amount, presence: true, numericality: { greater_than: 0 }
  validates :payment_method, presence: true

  scope :pending, -> { where(status: 'pending') }
  scope :completed, -> { where(status: 'completed') }
  scope :failed, -> { where(status: 'failed') }
  scope :rejected, -> { where(status: 'rejected') }

  def complete!
    update!(status: 'completed', processed_at: Time.current)
  end

  def reject!(reason = nil)
    update!(status: 'rejected', processed_at: Time.current)
  end

  def can_be_processed?
    pending? && order.can_accept_payment?
  end
end

class PaymentProcessor
  def initialize(payment)
    @payment = payment
  end

  def process
    return reject_payment('Order expired') unless @payment.can_be_processed?
    
    # Payment processing logic would go here
    @payment.complete!
  end

  private

  def reject_payment(reason)
    @payment.reject!(reason)
  end
end
```