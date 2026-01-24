# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: payments
#
#  id                :bigint           not null, primary key
#  amount_cents      :integer          not null
#  currency          :string           default("USD"), not null
#  status            :string           not null
#  payment_method    :string           not null
#  processed_at      :datetime
#  user_id           :bigint           not null
#  order_id          :bigint           not null
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#
# Table name: orders
#
#  id                :bigint           not null, primary key
#  total_cents       :integer          not null
#  currency          :string           default("USD"), not null
#  status            :string           not null
#  user_id           :bigint           not null
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#
# Table name: notifications
#
#  id                :bigint           not null, primary key
#  user_id           :bigint           not null
#  notifiable_type   :string           not null
#  notifiable_id     :bigint           not null
#  notification_type :string           not null
#  status            :string           default("pending"), not null
#  sent_at           :datetime
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
```

## Models

```ruby
class Payment < ApplicationRecord
  belongs_to :user
  belongs_to :order
  has_many :notifications, as: :notifiable, dependent: :destroy

  enum status: {
    pending: 'pending',
    processing: 'processing',
    confirmed: 'confirmed',
    failed: 'failed',
    refunded: 'refunded'
  }

  enum payment_method: {
    credit_card: 'credit_card',
    bank_transfer: 'bank_transfer',
    paypal: 'paypal'
  }

  scope :confirmed, -> { where(status: 'confirmed') }
  scope :recent, -> { order(created_at: :desc) }

  def amount
    Money.new(amount_cents, currency)
  end

  def confirm!
    update!(status: 'confirmed', processed_at: Time.current)
  end
end

class Order < ApplicationRecord
  belongs_to :user
  has_many :payments, dependent: :destroy

  enum status: {
    pending: 'pending',
    paid: 'paid',
    shipped: 'shipped',
    delivered: 'delivered',
    cancelled: 'cancelled'
  }

  def total
    Money.new(total_cents, currency)
  end
end

class Notification < ApplicationRecord
  belongs_to :user
  belongs_to :notifiable, polymorphic: true

  enum status: {
    pending: 'pending',
    sent: 'sent',
    failed: 'failed'
  }

  enum notification_type: {
    payment_confirmation: 'payment_confirmation',
    order_shipped: 'order_shipped',
    order_delivered: 'order_delivered'
  }

  scope :pending, -> { where(status: 'pending') }
  scope :for_type, ->(type) { where(notification_type: type) }

  def mark_as_sent!
    update!(status: 'sent', sent_at: Time.current)
  end
end

class User < ApplicationRecord
  has_many :payments, dependent: :destroy
  has_many :orders, dependent: :destroy
  has_many :notifications, dependent: :destroy

  def email_notifications_enabled?
    preferences['email_notifications'] != false
  end
end
```