# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id            :bigint           not null, primary key
#  email         :string           not null
#  name          :string
#  status        :string           default("active"), not null
#  updated_by_id :bigint
#  created_at    :datetime         not null
#  updated_at    :datetime         not null
#
# Indexes
#
#  index_users_on_email   (email) UNIQUE
#  index_users_on_status  (status)
#

# Table name: activity_logs
#
#  id             :bigint           not null, primary key
#  action         :string           not null
#  performed_by_id :bigint          not null
#  details        :jsonb            default({})
#  created_at     :datetime         not null
#
# Indexes
#
#  index_activity_logs_on_performed_by_id  (performed_by_id)
#  index_activity_logs_on_action           (action)
#
```

## Models

```ruby
class User < ApplicationRecord
  belongs_to :updated_by, class_name: 'User', optional: true
  has_many :activity_logs, foreign_key: :performed_by_id

  STATUSES = %w[active inactive suspended].freeze

  validates :email, presence: true, uniqueness: true
  validates :status, inclusion: { in: STATUSES }

  scope :active, -> { where(status: 'active') }
  scope :inactive, -> { where(status: 'inactive') }
  scope :suspended, -> { where(status: 'suspended') }

  after_update :send_status_notification, if: :saved_change_to_status?

  private

  def send_status_notification
    UserStatusMailer.status_changed(self).deliver_later
  end
end

class ActivityLog < ApplicationRecord
  belongs_to :performed_by, class_name: 'User'

  validates :action, presence: true
end
```
