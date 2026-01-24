# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: notifications
#
#  id           :bigint           not null, primary key
#  user_id      :bigint           not null
#  title        :string           not null
#  body         :text
#  notification_type :string      not null
#  status       :string           default("pending"), not null
#  metadata     :jsonb
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Indexes
#
#  index_notifications_on_user_id  (user_id)
#  index_notifications_on_status   (status)
#

# Table name: notification_deliveries
#
#  id              :bigint           not null, primary key
#  notification_id :bigint           not null
#  delivery_method :string           not null
#  status          :string           default("pending"), not null
#  error_message   :text
#  attempted_at    :datetime
#  delivered_at    :datetime
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
#
# Indexes
#
#  index_notification_deliveries_on_notification_id  (notification_id)
#  index_notification_deliveries_on_status           (status)
#
```

## Models

```ruby
class Notification < ApplicationRecord
  STATUSES = %w[pending processing delivered failed].freeze
  TYPES = %w[welcome order_confirmation password_reset promotion].freeze

  belongs_to :user
  has_many :notification_deliveries, dependent: :destroy

  validates :title, presence: true
  validates :notification_type, inclusion: { in: TYPES }
  validates :status, inclusion: { in: STATUSES }

  scope :pending, -> { where(status: 'pending') }
  scope :failed, -> { where(status: 'failed') }
  scope :for_delivery, -> { where(status: %w[pending failed]) }

  def mark_as_processing!
    update!(status: 'processing')
  end

  def mark_as_delivered!
    update!(status: 'delivered')
  end

  def mark_as_failed!
    update!(status: 'failed')
  end

  def delivery_channels
    case notification_type
    when 'welcome', 'password_reset'
      %w[email]
    when 'order_confirmation'
      %w[email sms]
    when 'promotion'
      %w[email push_notification]
    else
      %w[email]
    end
  end
end

class NotificationDelivery < ApplicationRecord
  STATUSES = %w[pending processing delivered failed].freeze
  DELIVERY_METHODS = %w[email sms push_notification].freeze

  belongs_to :notification

  validates :delivery_method, inclusion: { in: DELIVERY_METHODS }
  validates :status, inclusion: { in: STATUSES }

  scope :pending, -> { where(status: 'pending') }
  scope :failed, -> { where(status: 'failed') }

  def mark_as_processing!
    update!(status: 'processing', attempted_at: Time.current)
  end

  def mark_as_delivered!
    update!(status: 'delivered', delivered_at: Time.current)
  end

  def mark_as_failed!(error)
    update!(
      status: 'failed',
      error_message: error.message,
      attempted_at: Time.current
    )
  end
end

class NotificationService
  def self.create_and_deliver(user:, type:, title:, body: nil, metadata: {})
    notification = Notification.create!(
      user: user,
      notification_type: type,
      title: title,
      body: body,
      metadata: metadata
    )

    DeliverNotificationJob.perform_async(notification.id)
    notification
  end
end
```