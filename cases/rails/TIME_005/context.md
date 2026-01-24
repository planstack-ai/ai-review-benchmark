# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: billing_cycles
#
#  id                :bigint           not null, primary key
#  start_date        :date             not null
#  end_date          :date             not null
#  status            :string           default("pending")
#  processed_at      :datetime
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#
# Table name: subscriptions
#
#  id                :bigint           not null, primary key
#  user_id           :bigint           not null
#  plan_id           :bigint           not null
#  billing_day       :integer          not null
#  status            :string           default("active")
#  next_billing_date :date
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#
# Table name: invoices
#
#  id                :bigint           not null, primary key
#  subscription_id   :bigint           not null
#  billing_cycle_id  :bigint
#  amount_cents      :integer          not null
#  due_date          :date             not null
#  status            :string           default("pending")
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
```

## Models

```ruby
class BillingCycle < ApplicationRecord
  STATUSES = %w[pending processing completed failed].freeze

  has_many :invoices, dependent: :nullify
  
  validates :start_date, :end_date, presence: true
  validates :status, inclusion: { in: STATUSES }
  
  scope :pending, -> { where(status: 'pending') }
  scope :for_month, ->(date) { where(start_date: date.beginning_of_month..date.end_of_month) }
  scope :completed, -> { where(status: 'completed') }
  
  def self.current_month
    today = Date.current
    for_month(today).first || create_for_month(today)
  end
  
  def self.create_for_month(date)
    create!(
      start_date: date.beginning_of_month,
      end_date: date.end_of_month,
      status: 'pending'
    )
  end
  
  def mark_as_processing!
    update!(status: 'processing', processed_at: Time.current)
  end
  
  def complete!
    update!(status: 'completed')
  end
end

class Subscription < ApplicationRecord
  STATUSES = %w[active paused cancelled].freeze
  
  belongs_to :user
  belongs_to :plan
  has_many :invoices, dependent: :destroy
  
  validates :billing_day, inclusion: { in: 1..31 }
  validates :status, inclusion: { in: STATUSES }
  
  scope :active, -> { where(status: 'active') }
  scope :due_for_billing, ->(date) { 
    active.where('next_billing_date <= ?', date)
  }
  
  def calculate_next_billing_date(from_date = Date.current)
    target_month = from_date.next_month
    safe_billing_day = [billing_day, target_month.end_of_month.day].min
    target_month.beginning_of_month + (safe_billing_day - 1).days
  end
  
  def update_next_billing_date!
    update!(next_billing_date: calculate_next_billing_date)
  end
end

class Invoice < ApplicationRecord
  STATUSES = %w[pending paid failed].freeze
  
  belongs_to :subscription
  belongs_to :billing_cycle, optional: true
  
  validates :amount_cents, presence: true, numericality: { greater_than: 0 }
  validates :due_date, presence: true
  validates :status, inclusion: { in: STATUSES }
  
  scope :pending, -> { where(status: 'pending') }
  scope :for_cycle, ->(cycle) { where(billing_cycle: cycle) }
  
  def amount
    Money.new(amount_cents)
  end
end
```