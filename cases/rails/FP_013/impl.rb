# frozen_string_literal: true

class BulkUserStatusUpdateService
  attr_reader :user_ids, :status, :updated_by, :errors

  def initialize(user_ids:, status:, updated_by:)
    @user_ids = Array(user_ids)
    @status = status
    @updated_by = updated_by
    @errors = []
  end

  def call
    return failure('No user IDs provided') if user_ids.empty?
    return failure('Invalid status') unless valid_status?
    return failure('Updated by user is required') unless updated_by

    ActiveRecord::Base.transaction do
      validate_users_exist
      return failure(errors.join(', ')) if errors.any?

      perform_bulk_update
      log_bulk_update_activity
    end

    success
  rescue ActiveRecord::RecordInvalid => e
    failure("Database error: #{e.message}")
  end

  private

  def valid_status?
    %w[active inactive suspended].include?(status)
  end

  def validate_users_exist
    existing_ids = User.where(id: user_ids).pluck(:id)
    missing_ids = user_ids - existing_ids
    
    if missing_ids.any?
      errors << "Users not found: #{missing_ids.join(', ')}"
    end
  end

  def perform_bulk_update
    User.where(id: user_ids).update_all(
      status: status,
      updated_at: Time.current,
      updated_by_id: updated_by.id
    )
  end

  def log_bulk_update_activity
    ActivityLog.create!(
      action: 'bulk_status_update',
      performed_by: updated_by,
      details: {
        user_count: user_ids.length,
        new_status: status,
        user_ids: user_ids
      },
      created_at: Time.current
    )
  end

  def success
    OpenStruct.new(
      success?: true,
      updated_count: user_ids.length,
      message: "Successfully updated #{user_ids.length} users to #{status}"
    )
  end

  def failure(message)
    OpenStruct.new(
      success?: false,
      updated_count: 0,
      message: message,
      errors: errors
    )
  end
end