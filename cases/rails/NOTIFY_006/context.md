# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: notifications
#
#  id           :bigint           not null, primary key
#  user_id      :bigint           not null
#  type         :string           not null
#  subject      :string           not null
#  body         :text
#  status       :string           default("pending"), not null
#  scheduled_at :datetime
#  sent_at      :datetime
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Indexes
#
#  index_notifications_on_user_id                    (user_id)
#  index_notifications_on_status_and_scheduled_at    (status,scheduled_at)
#  index_notifications_on_type_and_created_at        (type,created_at)
#

# Table name: users
#
#  id           :bigint           not null, primary key
#  email        :string           not null
#  provider     :string           default("sendgrid")
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
```

## Models

```ruby
class User < ApplicationRecord
  has_many :notifications, dependent: :destroy
  
  validates :email, presence: true, uniqueness: true
  validates :provider, inclusion: { in: %w[sendgrid mailgun ses] }
  
  scope :by_provider, ->(provider) { where(provider: provider) }
end

class Notification < ApplicationRecord
  belongs_to :user
  
  STATUSES = %w[pending processing sent failed].freeze
  TYPES = %w[welcome password_reset newsletter promotion].freeze
  
  validates :type, inclusion: { in: TYPES }
  validates :status, inclusion: { in: STATUSES }
  validates :subject, :body, presence: true
  
  scope :pending, -> { where(status: 'pending') }
  scope :ready_to_send, -> { pending.where('scheduled_at IS NULL OR scheduled_at <= ?', Time.current) }
  scope :by_type, ->(type) { where(type: type) }
  scope :created_after, ->(time) { where('created_at > ?', time) }
  
  def mark_as_processing!
    update!(status: 'processing')
  end
  
  def mark_as_sent!
    update!(status: 'sent', sent_at: Time.current)
  end
  
  def mark_as_failed!
    update!(status: 'failed')
  end
end

class EmailProviderConfig
  RATE_LIMITS = {
    'sendgrid' => { per_hour: 100, per_minute: 10 },
    'mailgun' => { per_hour: 300, per_minute: 20 },
    'ses' => { per_hour: 200, per_minute: 14 }
  }.freeze
  
  def self.rate_limit_for(provider)
    RATE_LIMITS[provider] || RATE_LIMITS['sendgrid']
  end
  
  def self.hourly_limit(provider)
    rate_limit_for(provider)[:per_hour]
  end
  
  def self.minute_limit(provider)
    rate_limit_for(provider)[:per_minute]
  end
end

class NotificationMailer < ApplicationMailer
  def send_notification(notification)
    @notification = notification
    mail(
      to: notification.user.email,
      subject: notification.subject,
      body: notification.body
    )
  end
end
```