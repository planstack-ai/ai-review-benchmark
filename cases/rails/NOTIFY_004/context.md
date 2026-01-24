# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  first_name :string
#  last_name  :string
#  phone      :string
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: notifications
#
#  id           :bigint           not null, primary key
#  user_id      :bigint           not null
#  template_key :string           not null
#  subject      :string           not null
#  body         :text             not null
#  sent_at      :datetime
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: email_templates
#
#  id           :bigint           not null, primary key
#  key          :string           not null, index: true
#  subject      :string           not null
#  body         :text             not null
#  variables    :json
#  active       :boolean          default: true
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :notifications, dependent: :destroy
  
  validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  
  def full_name
    return nil if first_name.blank? && last_name.blank?
    [first_name, last_name].compact.join(' ')
  end
  
  def display_name
    full_name.presence || email.split('@').first
  end
end

class EmailTemplate < ApplicationRecord
  validates :key, presence: true, uniqueness: true
  validates :subject, :body, presence: true
  
  scope :active, -> { where(active: true) }
  
  WELCOME_EMAIL = 'welcome_email'.freeze
  PASSWORD_RESET = 'password_reset'.freeze
  ORDER_CONFIRMATION = 'order_confirmation'.freeze
  
  def variable_names
    variables&.map(&:to_s) || []
  end
end

class Notification < ApplicationRecord
  belongs_to :user
  
  validates :template_key, :subject, :body, presence: true
  
  scope :sent, -> { where.not(sent_at: nil) }
  scope :pending, -> { where(sent_at: nil) }
  
  def sent?
    sent_at.present?
  end
  
  def mark_as_sent!
    update!(sent_at: Time.current)
  end
end

class NotificationMailer < ApplicationMailer
  default from: 'noreply@example.com'
  
  def send_notification(notification)
    @notification = notification
    @user = notification.user
    
    mail(
      to: @user.email,
      subject: @notification.subject
    )
  end
end
```