# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id                     :bigint           not null, primary key
#  email                  :string           not null
#  first_name             :string
#  last_name              :string
#  status                 :integer          default("active")
#  email_verified_at      :datetime
#  last_login_at          :datetime
#  created_at             :datetime         not null
#  updated_at             :datetime         not null
#
# Indexes
#
#  index_users_on_email   (email) UNIQUE
#

# Table name: user_profiles
#
#  id                     :bigint           not null, primary key
#  user_id                :bigint           not null
#  bio                    :text
#  avatar_url             :string
#  preferences            :jsonb
#  created_at             :datetime         not null
#  updated_at             :datetime         not null
#
# Indexes
#
#  index_user_profiles_on_user_id  (user_id)
#

# Table name: audit_logs
#
#  id                     :bigint           not null, primary key
#  auditable_type         :string
#  auditable_id           :bigint
#  action                 :string
#  changes                :jsonb
#  user_id                :bigint
#  created_at             :datetime         not null
#
# Indexes
#
#  index_audit_logs_on_auditable  (auditable_type,auditable_id)
#  index_audit_logs_on_user_id    (user_id)
```

## Models

```ruby
class User < ApplicationRecord
  enum status: { active: 0, inactive: 1, suspended: 2 }

  has_one :user_profile, dependent: :destroy
  has_many :audit_logs, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :first_name, :last_name, presence: true

  scope :verified, -> { where.not(email_verified_at: nil) }
  scope :recent_login, -> { where('last_login_at > ?', 30.days.ago) }

  def full_name
    "#{first_name} #{last_name}".strip
  end

  def verified?
    email_verified_at.present?
  end

  private

  def normalize_email
    self.email = email.downcase.strip if email.present?
  end

  def send_welcome_email
    UserMailer.welcome(self).deliver_later
  end

  def create_default_profile
    build_user_profile(preferences: default_preferences)
  end

  def default_preferences
    {
      notifications: true,
      theme: 'light',
      language: 'en'
    }
  end
end

class UserProfile < ApplicationRecord
  belongs_to :user

  validates :bio, length: { maximum: 500 }

  def avatar_present?
    avatar_url.present?
  end

  def notification_enabled?
    preferences.dig('notifications') == true
  end
end

class AuditLog < ApplicationRecord
  belongs_to :auditable, polymorphic: true
  belongs_to :user, optional: true

  validates :action, presence: true

  scope :for_model, ->(model) { where(auditable: model) }
  scope :recent, -> { where('created_at > ?', 7.days.ago) }

  def self.log_action(auditable, action, changes = {}, current_user = nil)
    create!(
      auditable: auditable,
      action: action,
      changes: changes,
      user: current_user
    )
  end
end
```