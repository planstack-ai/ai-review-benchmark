# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  user_id      :bigint           not null
#  status       :string           default("pending"), not null
#  total_amount :decimal(10,2)    not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
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
#  user_id      :bigint           not null
#  message      :text             not null
#  notification_type :string      not null
#  read_at      :datetime
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :orders, dependent: :destroy
  has_many :notifications, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true

  scope :active, -> { where.not(deleted_at: nil) }
end

class Order < ApplicationRecord
  belongs_to :user

  validates :status, inclusion: { in: %w[pending processing completed cancelled] }
  validates :total_amount, presence: true, numericality: { greater_than: 0 }

  scope :pending, -> { where(status: 'pending') }
  scope :completed, -> { where(status: 'completed') }

  def complete!
    update!(status: 'completed')
  end

  def cancel!
    update!(status: 'cancelled')
  end

  private

  def send_completion_notification
    NotificationJob.perform_later(user_id, "Your order ##{id} has been completed!")
  end

  def send_cancellation_notification
    NotificationJob.perform_later(user_id, "Your order ##{id} has been cancelled.")
  end
end

class Notification < ApplicationRecord
  belongs_to :user

  validates :message, presence: true
  validates :notification_type, presence: true

  scope :unread, -> { where(read_at: nil) }
  scope :recent, -> { order(created_at: :desc) }

  def mark_as_read!
    update!(read_at: Time.current)
  end
end
```

## Jobs

```ruby
class NotificationJob < ApplicationJob
  queue_as :default

  def perform(user_id, message)
    user = User.find(user_id)
    Notification.create!(
      user: user,
      message: message,
      notification_type: 'order_update'
    )
  end
end

class EmailNotificationJob < ApplicationJob
  queue_as :mailers

  def perform(user_id, subject, body)
    user = User.find(user_id)
    UserMailer.notification(user, subject, body).deliver_now
  end
end
```