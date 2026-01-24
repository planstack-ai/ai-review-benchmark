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
#  status     :string           default("active")
#  last_login :datetime
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: posts
#
#  id          :bigint           not null, primary key
#  title       :string           not null
#  content     :text
#  status      :string           default("draft")
#  user_id     :bigint           not null
#  published_at :datetime
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Table name: notifications
#
#  id         :bigint           not null, primary key
#  user_id    :bigint           not null
#  message    :string           not null
#  read       :boolean          default(false)
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :posts, dependent: :destroy
  has_many :notifications, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true

  enum status: { active: 'active', inactive: 'inactive', suspended: 'suspended' }

  scope :active, -> { where(status: 'active') }
  scope :recently_active, -> { where('last_login > ?', 1.week.ago) }

  after_update :send_status_change_notification, if: :saved_change_to_status?
  after_update :log_login_activity, if: :saved_change_to_last_login?

  private

  def send_status_change_notification
    return unless status_previously_changed?
    
    UserMailer.status_changed(self).deliver_later
    create_system_notification("Your account status has been updated to #{status}")
  end

  def log_login_activity
    Rails.logger.info "User #{id} logged in at #{last_login}"
    update_login_streak
  end

  def create_system_notification(message)
    notifications.create!(message: message)
  end

  def update_login_streak
    # Complex login streak calculation logic
  end
end

class Post < ApplicationRecord
  belongs_to :user

  validates :title, presence: true
  validates :user_id, presence: true

  enum status: { draft: 'draft', published: 'published', archived: 'archived' }

  scope :published, -> { where(status: 'published') }
  scope :recent, -> { where('created_at > ?', 1.month.ago) }

  before_update :set_published_at, if: :will_save_change_to_status?
  after_update :notify_followers, if: :saved_change_to_status?
  after_update :update_search_index

  private

  def set_published_at
    if status_changed? && status == 'published'
      self.published_at = Time.current
    end
  end

  def notify_followers
    return unless status_previously_changed? && published?
    
    NotifyFollowersJob.perform_later(self)
  end

  def update_search_index
    SearchIndexJob.perform_later(self)
  end
end

class Notification < ApplicationRecord
  belongs_to :user

  validates :message, presence: true

  scope :unread, -> { where(read: false) }
  scope :recent, -> { where('created_at > ?', 1.week.ago) }

  after_create :send_push_notification
  after_update :mark_as_processed, if: :saved_change_to_read?

  private

  def send_push_notification
    PushNotificationService.new(user, message).deliver
  end

  def mark_as_processed
    Rails.logger.info "Notification #{id} marked as read by user #{user_id}"
  end
end
```