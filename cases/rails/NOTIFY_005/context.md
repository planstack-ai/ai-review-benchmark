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
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: notifications
#
#  id           :bigint           not null, primary key
#  recipient_id :bigint           not null
#  sender_id    :bigint
#  subject      :string           not null
#  body         :text
#  sent_at      :datetime
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: notification_deliveries
#
#  id              :bigint           not null, primary key
#  notification_id :bigint           not null
#  email_address   :string           not null
#  delivered_at    :datetime
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  validates :email, presence: true, uniqueness: true
  validates :name, presence: true

  has_many :sent_notifications, class_name: 'Notification', foreign_key: 'sender_id'
  has_many :received_notifications, class_name: 'Notification', foreign_key: 'recipient_id'

  scope :active, -> { where(active: true) }

  def display_name
    name.present? ? name : email.split('@').first
  end
end

class Notification < ApplicationRecord
  belongs_to :recipient, class_name: 'User'
  belongs_to :sender, class_name: 'User', optional: true
  has_many :notification_deliveries, dependent: :destroy

  validates :subject, presence: true
  validates :recipient_id, presence: true

  scope :pending, -> { where(sent_at: nil) }
  scope :sent, -> { where.not(sent_at: nil) }

  def delivered?
    notification_deliveries.where.not(delivered_at: nil).exists?
  end

  def mark_as_sent!
    update!(sent_at: Time.current)
  end
end

class NotificationDelivery < ApplicationRecord
  belongs_to :notification

  validates :email_address, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }

  scope :delivered, -> { where.not(delivered_at: nil) }
  scope :pending, -> { where(delivered_at: nil) }

  def mark_as_delivered!
    update!(delivered_at: Time.current)
  end
end

class NotificationMailer < ApplicationMailer
  default from: 'notifications@example.com'

  def notification_email(notification_id, recipient_email)
    @notification = Notification.find(notification_id)
    @recipient = @notification.recipient
    
    mail(
      to: recipient_email,
      subject: @notification.subject
    )
  end
end
```