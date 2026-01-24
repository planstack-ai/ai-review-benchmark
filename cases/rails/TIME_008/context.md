# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id              :bigint           not null, primary key
#  order_number    :string           not null
#  customer_id     :bigint           not null
#  delivery_date   :date
#  status          :string           default("pending")
#  total_amount    :decimal(10,2)
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
#
# Indexes
#
#  index_orders_on_customer_id    (customer_id)
#  index_orders_on_delivery_date  (delivery_date)
#  index_orders_on_order_number   (order_number) UNIQUE
#

# Table name: customers
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  email      :string           not null
#  phone      :string
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
```

## Models

```ruby
class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class

  private

  def date_in_future?(date)
    return false if date.blank?
    date > Date.current
  end

  def add_date_error(attribute, message = "must be in the future")
    errors.add(attribute, message)
  end
end

class Customer < ApplicationRecord
  has_many :orders, dependent: :destroy

  validates :name, presence: true
  validates :email, presence: true, uniqueness: true
end

class Order < ApplicationRecord
  VALID_STATUSES = %w[pending confirmed shipped delivered cancelled].freeze

  belongs_to :customer

  validates :order_number, presence: true, uniqueness: true
  validates :status, inclusion: { in: VALID_STATUSES }
  validates :total_amount, presence: true, numericality: { greater_than: 0 }

  scope :pending, -> { where(status: 'pending') }
  scope :confirmed, -> { where(status: 'confirmed') }
  scope :with_delivery_date, -> { where.not(delivery_date: nil) }
  scope :scheduled_for_date, ->(date) { where(delivery_date: date) }

  before_validation :generate_order_number, if: -> { order_number.blank? }

  def confirmed?
    status == 'confirmed'
  end

  def requires_delivery_date?
    %w[confirmed shipped].include?(status)
  end

  def past_due?
    delivery_date.present? && delivery_date < Date.current
  end

  private

  def generate_order_number
    self.order_number = "ORD-#{SecureRandom.hex(4).upcase}"
  end
end
```