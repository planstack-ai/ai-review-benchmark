# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  name       :string           not null
#  timezone   :string           default("UTC")
#  created_at :datetime         not null
#  updated_at :datetime         not null
#

# Table name: events
#
#  id          :bigint           not null, primary key
#  title       :string           not null
#  description :text
#  starts_at   :datetime         not null
#  ends_at     :datetime
#  user_id     :bigint           not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#

# Table name: notifications
#
#  id         :bigint           not null, primary key
#  message    :string           not null
#  sent_at    :datetime         not null
#  user_id    :bigint           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
```

## Models

```ruby
class User < ApplicationRecord
  has_many :events, dependent: :destroy
  has_many :notifications, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true
  validates :timezone, inclusion: { in: ActiveSupport::TimeZone.all.map(&:name) }

  def time_zone
    ActiveSupport::TimeZone[timezone]
  end

  def local_time(utc_time)
    utc_time.in_time_zone(timezone)
  end
end

class Event < ApplicationRecord
  belongs_to :user

  validates :title, presence: true
  validates :starts_at, presence: true
  validate :ends_at_after_starts_at, if: :ends_at?

  scope :upcoming, -> { where('starts_at > ?', Time.current) }
  scope :today, -> { where(starts_at: Date.current.all_day) }
  scope :this_week, -> { where(starts_at: Date.current.beginning_of_week..Date.current.end_of_week) }

  private

  def ends_at_after_starts_at
    return unless ends_at && starts_at

    errors.add(:ends_at, 'must be after start time') if ends_at <= starts_at
  end
end

class Notification < ApplicationRecord
  belongs_to :user

  validates :message, presence: true
  validates :sent_at, presence: true

  scope :recent, -> { where('sent_at > ?', 1.week.ago) }
  scope :today, -> { where(sent_at: Date.current.all_day) }
end

class ApplicationController < ActionController::Base
  before_action :authenticate_user!
  before_action :set_time_zone

  private

  def set_time_zone
    Time.zone = current_user&.timezone || 'UTC'
  end
end
```