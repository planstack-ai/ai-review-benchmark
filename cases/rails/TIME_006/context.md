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
#  ends_at     :datetime         not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#  user_id     :bigint           not null
#
# Table name: subscriptions
#
#  id         :bigint           not null, primary key
#  user_id    :bigint           not null
#  plan_type  :string           not null
#  starts_at  :datetime         not null
#  ends_at    :datetime
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: reports
#
#  id           :bigint           not null, primary key
#  report_type  :string           not null
#  period_start :datetime         not null
#  period_end   :datetime         not null
#  data         :jsonb
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
```

## Models

```ruby
class Event < ApplicationRecord
  belongs_to :user
  
  validates :title, presence: true
  validates :starts_at, :ends_at, presence: true
  validate :ends_after_starts
  
  scope :in_date_range, ->(start_date, end_date) {
    where(starts_at: start_date.beginning_of_day..end_date.end_of_day)
  }
  
  scope :current_year, -> { where(starts_at: Time.current.beginning_of_year..Time.current.end_of_year) }
  scope :previous_year, -> { where(starts_at: 1.year.ago.beginning_of_year..1.year.ago.end_of_year) }
  
  def duration_in_hours
    ((ends_at - starts_at) / 1.hour).round(2)
  end
  
  def spans_multiple_days?
    starts_at.to_date != ends_at.to_date
  end
  
  private
  
  def ends_after_starts
    return unless starts_at && ends_at
    errors.add(:ends_at, "must be after start time") if ends_at <= starts_at
  end
end

class Subscription < ApplicationRecord
  belongs_to :user
  
  PLAN_TYPES = %w[basic premium enterprise].freeze
  
  validates :plan_type, inclusion: { in: PLAN_TYPES }
  validates :starts_at, presence: true
  validate :ends_after_starts, if: :ends_at?
  
  scope :active, -> { where(ends_at: nil).or(where("ends_at > ?", Time.current)) }
  scope :expired, -> { where("ends_at < ?", Time.current) }
  scope :ending_soon, ->(days = 30) { where(ends_at: Time.current..(days.days.from_now)) }
  
  def active?
    ends_at.nil? || ends_at > Time.current
  end
  
  def days_remaining
    return Float::INFINITY if ends_at.nil?
    [(ends_at.to_date - Date.current).to_i, 0].max
  end
  
  private
  
  def ends_after_starts
    errors.add(:ends_at, "must be after start date") if ends_at <= starts_at
  end
end

class Report < ApplicationRecord
  REPORT_TYPES = %w[monthly quarterly yearly].freeze
  
  validates :report_type, inclusion: { in: REPORT_TYPES }
  validates :period_start, :period_end, presence: true
  validate :period_end_after_start
  
  scope :for_period, ->(start_date, end_date) {
    where("period_start <= ? AND period_end >= ?", end_date, start_date)
  }
  
  scope :monthly, -> { where(report_type: 'monthly') }
  scope :quarterly, -> { where(report_type: 'quarterly') }
  scope :yearly, -> { where(report_type: 'yearly') }
  
  def period_duration_days
    (period_end.to_date - period_start.to_date).to_i + 1
  end
  
  def includes_date?(date)
    date.to_date.between?(period_start.to_date, period_end.to_date)
  end
  
  private
  
  def period_end_after_start
    return unless period_start && period_end
    errors.add(:period_end, "must be after period start") if period_end < period_start
  end
end
```