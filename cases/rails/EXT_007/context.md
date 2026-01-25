# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: audit_logs
#
#  id           :bigint           not null, primary key
#  user_id      :bigint           not null
#  action       :string           not null
#  resource_type :string          not null
#  resource_id   :bigint          not null
#  metadata     :jsonb
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Indexes
#
#  index_audit_logs_on_user_id                    (user_id)
#  index_audit_logs_on_resource_type_and_resource_id (resource_type,resource_id)
#  index_audit_logs_on_created_at                 (created_at)

# Table name: background_jobs
#
#  id         :bigint           not null, primary key
#  job_type   :string           not null
#  status     :string           default("pending")
#  payload    :jsonb
#  scheduled_at :datetime
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class AuditLog < ApplicationRecord
  belongs_to :user
  belongs_to :resource, polymorphic: true

  validates :action, presence: true
  validates :resource_type, presence: true
  validates :resource_id, presence: true

  scope :recent, -> { order(created_at: :desc) }
  scope :for_user, ->(user) { where(user: user) }
  scope :for_resource, ->(resource) { where(resource: resource) }
  scope :by_action, ->(action) { where(action: action) }

  BATCH_SIZE = 1000
  MAX_RETRY_ATTEMPTS = 3

  def self.log_action(user:, action:, resource:, metadata: {})
    create!(
      user: user,
      action: action,
      resource: resource,
      metadata: metadata
    )
  end

  def self.bulk_insert(records)
    insert_all(records, returning: false)
  end
end

class BackgroundJob < ApplicationRecord
  enum status: { pending: 'pending', processing: 'processing', completed: 'completed', failed: 'failed' }

  scope :ready_for_processing, -> { pending.where('scheduled_at <= ?', Time.current) }
  scope :stale, -> { processing.where('updated_at < ?', 1.hour.ago) }

  validates :job_type, presence: true

  def mark_processing!
    update!(status: 'processing', updated_at: Time.current)
  end

  def mark_completed!
    update!(status: 'completed')
  end

  def mark_failed!
    update!(status: 'failed')
  end
end

class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class

  def self.with_advisory_lock(key, &block)
    connection.with_advisory_lock(key, &block)
  end
end

module Auditable
  extend ActiveSupport::Concern

  included do
    after_create :log_create_action
    after_update :log_update_action
    after_destroy :log_destroy_action
  end

  private

  def log_create_action
    AuditLog.log_action(
      user: Current.user,
      action: 'create',
      resource: self
    )
  end

  def log_update_action
    return unless saved_changes.any?
    
    AuditLog.log_action(
      user: Current.user,
      action: 'update',
      resource: self,
      metadata: { changes: saved_changes }
    )
  end

  def log_destroy_action
    AuditLog.log_action(
      user: Current.user,
      action: 'destroy',
      resource: self
    )
  end
end
```