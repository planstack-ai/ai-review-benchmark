# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  user_id      :bigint           not null
#  total        :decimal(10,2)    not null
#  status       :string           default("pending"), not null
#  payment_ref  :string
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy

  validates :total, presence: true, numericality: { greater_than: 0 }
  validates :status, inclusion: { in: %w[pending processing paid failed refunded] }

  scope :pending, -> { where(status: 'pending') }
  scope :paid, -> { where(status: 'paid') }
end
```

## PaymentGateway Interface

```ruby
# External payment gateway client
# Note: This makes HTTP calls to external payment provider
module PaymentGateway
  class ChargeResult
    attr_reader :id, :status, :amount

    def initialize(id:, status:, amount:)
      @id = id
      @status = status
      @amount = amount
    end

    def success?
      status == 'succeeded'
    end
  end

  class PaymentError < StandardError; end

  # Charges the given amount
  # @param amount [Decimal] amount to charge
  # @return [ChargeResult] result of the charge operation
  # @raise [PaymentError] if payment fails
  # Note: This method makes an HTTP request to external API
  def self.charge(amount)
    # Implementation makes HTTP POST to payment provider
    # Typical latency: 500ms-3000ms
    # May timeout after 30 seconds
  end
end
```

## Usage Guidelines

- Use transactions to ensure atomic database updates
- External API calls (HTTP requests) should not be made inside database transactions as they can hold locks for extended periods
