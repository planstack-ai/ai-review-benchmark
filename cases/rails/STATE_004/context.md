# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  user_id      :bigint           not null
#  total_amount :decimal(10,2)    not null
#  status       :string           default("pending"), not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: payments
#
#  id                :bigint           not null, primary key
#  order_id          :bigint           not null
#  amount            :decimal(10,2)    not null
#  payment_method    :string           not null
#  transaction_id    :string
#  status            :string           default("pending"), not null
#  processed_at      :datetime
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#
# Table name: payment_attempts
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  amount     :decimal(10,2)    not null
#  status     :string           not null
#  error_code :string
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :payments, dependent: :destroy
  has_many :payment_attempts, dependent: :destroy

  STATUSES = %w[pending processing paid cancelled].freeze
  
  validates :status, inclusion: { in: STATUSES }
  validates :total_amount, presence: true, numericality: { greater_than: 0 }

  scope :pending, -> { where(status: 'pending') }
  scope :paid, -> { where(status: 'paid') }

  def pending?
    status == 'pending'
  end

  def paid?
    status == 'paid'
  end

  def mark_as_paid!
    update!(status: 'paid')
  end
end

class Payment < ApplicationRecord
  belongs_to :order

  STATUSES = %w[pending processing completed failed].freeze
  PAYMENT_METHODS = %w[credit_card paypal bank_transfer].freeze

  validates :status, inclusion: { in: STATUSES }
  validates :payment_method, inclusion: { in: PAYMENT_METHODS }
  validates :amount, presence: true, numericality: { greater_than: 0 }

  scope :completed, -> { where(status: 'completed') }
  scope :failed, -> { where(status: 'failed') }
  scope :pending, -> { where(status: 'pending') }

  def completed?
    status == 'completed'
  end

  def failed?
    status == 'failed'
  end

  def mark_as_completed!(transaction_id)
    update!(
      status: 'completed',
      transaction_id: transaction_id,
      processed_at: Time.current
    )
  end
end

class PaymentAttempt < ApplicationRecord
  belongs_to :order

  STATUSES = %w[initiated processing completed failed].freeze

  validates :status, inclusion: { in: STATUSES }
  validates :amount, presence: true, numericality: { greater_than: 0 }

  scope :completed, -> { where(status: 'completed') }
  scope :failed, -> { where(status: 'failed') }
end

class PaymentGateway
  class DuplicatePaymentError < StandardError; end
  class PaymentProcessingError < StandardError; end

  def self.process_payment(order, payment_params)
    new(order, payment_params).process
  end

  private

  def initialize(order, payment_params)
    @order = order
    @payment_params = payment_params
  end

  def process
    # Gateway processing logic would go here
    # Returns transaction_id on success
    "txn_#{SecureRandom.hex(8)}"
  end
end
```