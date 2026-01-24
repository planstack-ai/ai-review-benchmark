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
#  status            :string           not null
#  payment_method    :string           not null
#  external_id       :string
#  processed_at      :datetime
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#  order_id          :bigint           not null
#
# Table name: refunds
#
#  id                :bigint           not null, primary key
#  amount_cents      :integer          not null
#  currency          :string           not null
#  reason            :string
#  external_id       :string
#  processed_at      :datetime
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#  payment_id        :bigint           not null
#
```

## Models

```ruby
class Payment < ApplicationRecord
  belongs_to :order
  has_many :refunds, dependent: :destroy

  validates :amount_cents, presence: true, numericality: { greater_than: 0 }
  validates :currency, presence: true
  validates :status, presence: true, inclusion: { in: VALID_STATUSES }
  validates :payment_method, presence: true

  VALID_STATUSES = %w[
    pending
    processing
    completed
    failed
    cancelled
    partially_refunded
    fully_refunded
  ].freeze

  scope :completed, -> { where(status: 'completed') }
  scope :refundable, -> { where(status: %w[completed partially_refunded]) }
  scope :with_refunds, -> { joins(:refunds) }

  def amount
    Money.new(amount_cents, currency)
  end

  def total_refunded_amount
    Money.new(refunds.sum(:amount_cents), currency)
  end

  def refundable_amount
    amount - total_refunded_amount
  end

  def can_be_refunded?
    %w[completed partially_refunded].include?(status) && refundable_amount > 0
  end

  def fully_refunded?
    total_refunded_amount >= amount
  end

  def partially_refunded?
    total_refunded_amount > 0 && total_refunded_amount < amount
  end
end

class Refund < ApplicationRecord
  belongs_to :payment

  validates :amount_cents, presence: true, numericality: { greater_than: 0 }
  validates :currency, presence: true

  scope :processed, -> { where.not(processed_at: nil) }
  scope :pending, -> { where(processed_at: nil) }

  def amount
    Money.new(amount_cents, currency)
  end

  def processed?
    processed_at.present?
  end
end

class Order < ApplicationRecord
  has_many :payments, dependent: :destroy

  def total_amount
    Money.new(payments.sum(:amount_cents), 'USD')
  end
end
```