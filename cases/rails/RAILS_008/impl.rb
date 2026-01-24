# frozen_string_literal: true

class OrderArchivalService
  include ActiveModel::Validations

  attr_reader :user, :archive_reason, :cutoff_date

  validates :user, presence: true
  validates :archive_reason, presence: true, inclusion: { in: %w[expired cancelled inactive] }
  validates :cutoff_date, presence: true

  def initialize(user:, archive_reason:, cutoff_date: 6.months.ago)
    @user = user
    @archive_reason = archive_reason
    @cutoff_date = cutoff_date
  end

  def call
    return failure_result('Invalid parameters') unless valid?
    return failure_result('No orders found') if eligible_orders.empty?

    ActiveRecord::Base.transaction do
      archive_orders
      update_user_statistics
      send_notification
    end

    success_result
  rescue StandardError => e
    Rails.logger.error "OrderArchivalService failed: #{e.message}"
    failure_result('Archival process failed')
  end

  private

  def eligible_orders
    @eligible_orders ||= user.orders
                            .where('created_at < ?', cutoff_date)
                            .where(status: %w[pending processing])
                            .includes(:order_items, :payments)
  end

  def archive_orders
    eligible_orders.update_all(
      status: 'archived',
      archived_at: Time.current,
      archive_reason: archive_reason,
      updated_at: Time.current
    )
  end

  def update_user_statistics
    archived_count = eligible_orders.count
    user.increment!(:archived_orders_count, archived_count)
    user.touch(:last_archival_at)
  end

  def send_notification
    return unless should_notify_user?

    UserMailer.orders_archived(
      user: user,
      archived_count: eligible_orders.count,
      archive_reason: archive_reason
    ).deliver_later
  end

  def should_notify_user?
    user.notification_preferences['order_archival'] &&
      eligible_orders.count >= 5
  end

  def success_result
    {
      success: true,
      archived_count: eligible_orders.count,
      message: 'Orders successfully archived'
    }
  end

  def failure_result(message)
    {
      success: false,
      archived_count: 0,
      message: message
    }
  end
end