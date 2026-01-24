# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  order_number :string           not null
#  placed_at    :datetime         not null
#  status       :string           not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: deliveries
#
#  id                    :bigint           not null, primary key
#  order_id              :bigint           not null
#  estimated_delivery_at :datetime
#  actual_delivery_at    :datetime
#  delivery_method       :string           not null
#  created_at            :datetime         not null
#  updated_at            :datetime         not null
#
# Table name: business_day_configs
#
#  id         :bigint           not null, primary key
#  country    :string           not null
#  holiday    :date             not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  has_one :delivery, dependent: :destroy
  
  validates :order_number, presence: true, uniqueness: true
  validates :placed_at, presence: true
  validates :status, inclusion: { in: %w[pending processing shipped delivered cancelled] }
  
  scope :recent, -> { where(placed_at: 1.month.ago..) }
  scope :shipped, -> { where(status: 'shipped') }
  
  def business_days_since_placed
    BusinessDayCalculator.business_days_between(placed_at.to_date, Date.current)
  end
end

class Delivery < ApplicationRecord
  belongs_to :order
  
  DELIVERY_METHODS = %w[standard express overnight].freeze
  
  validates :delivery_method, inclusion: { in: DELIVERY_METHODS }
  
  scope :pending, -> { where(actual_delivery_at: nil) }
  scope :completed, -> { where.not(actual_delivery_at: nil) }
  
  def overdue?
    return false unless estimated_delivery_at
    return false if actual_delivery_at
    
    Date.current > estimated_delivery_at.to_date
  end
end

class BusinessDayConfig < ApplicationRecord
  validates :country, presence: true
  validates :holiday, presence: true, uniqueness: { scope: :country }
  
  scope :for_country, ->(country) { where(country: country) }
  scope :for_date_range, ->(start_date, end_date) { where(holiday: start_date..end_date) }
  
  DEFAULT_COUNTRY = 'US'.freeze
end

class BusinessDayCalculator
  WEEKEND_DAYS = [0, 6].freeze # Sunday, Saturday
  
  def self.business_days_between(start_date, end_date, country: BusinessDayConfig::DEFAULT_COUNTRY)
    return 0 if start_date >= end_date
    
    holidays = BusinessDayConfig.for_country(country)
                               .for_date_range(start_date, end_date)
                               .pluck(:holiday)
                               .to_set
    
    business_days = 0
    current_date = start_date
    
    while current_date < end_date
      unless weekend?(current_date) || holidays.include?(current_date)
        business_days += 1
      end
      current_date += 1.day
    end
    
    business_days
  end
  
  def self.weekend?(date)
    WEEKEND_DAYS.include?(date.wday)
  end
  
  private_class_method :weekend?
end
```