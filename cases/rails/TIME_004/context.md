# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: events
#
#  id          :bigint           not null, primary key
#  title       :string           not null
#  description :text
#  starts_at   :datetime         not null
#  ends_at     :datetime
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#  user_id     :bigint           not null
#

# Table name: bookings
#
#  id         :bigint           not null, primary key
#  event_id   :bigint           not null
#  user_id    :bigint           not null
#  booked_at  :datetime         not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#

# Table name: daily_reports
#
#  id           :bigint           not null, primary key
#  report_date  :date             not null
#  total_sales  :decimal(10,2)
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
```

## Models

```ruby
class Event < ApplicationRecord
  belongs_to :user
  has_many :bookings, dependent: :destroy

  validates :title, presence: true
  validates :starts_at, presence: true

  scope :upcoming, -> { where('starts_at > ?', Time.current) }
  scope :past, -> { where('starts_at < ?', Time.current) }
  scope :today, -> { where(starts_at: Time.current.beginning_of_day..Time.current.end_of_day) }

  def duration_in_hours
    return nil unless ends_at
    ((ends_at - starts_at) / 1.hour).round(2)
  end

  def same_day?(other_datetime)
    starts_at.to_date == other_datetime.to_date
  end
end

class Booking < ApplicationRecord
  belongs_to :event
  belongs_to :user

  validates :booked_at, presence: true

  scope :recent, -> { where('booked_at > ?', 1.week.ago) }
  scope :for_date, ->(date) { where(booked_at: date.beginning_of_day..date.end_of_day) }

  def booked_today?
    booked_at.to_date == Date.current
  end
end

class DailyReport < ApplicationRecord
  validates :report_date, presence: true, uniqueness: true
  validates :total_sales, presence: true, numericality: { greater_than_or_equal_to: 0 }

  scope :for_month, ->(date) { where(report_date: date.beginning_of_month..date.end_of_month) }
  scope :recent, -> { where('report_date >= ?', 30.days.ago.to_date) }

  def self.find_by_date(date)
    find_by(report_date: date.to_date)
  end

  def weekend?
    report_date.saturday? || report_date.sunday?
  end
end

class User < ApplicationRecord
  has_many :events, dependent: :destroy
  has_many :bookings, dependent: :destroy

  def events_on_date(date)
    events.where(starts_at: date.beginning_of_day..date.end_of_day)
  end

  def has_bookings_on?(date)
    bookings.exists?(booked_at: date.beginning_of_day..date.end_of_day)
  end
end
```