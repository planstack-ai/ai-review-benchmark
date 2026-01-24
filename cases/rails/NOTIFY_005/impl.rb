# frozen_string_literal: true

class OrderConfirmationService
  attr_reader :order, :user

  def initialize(order, user = nil)
    @order = order
    @user = user || current_admin_user
  end

  def call
    return failure_result('Order not found') unless order&.persisted?
    return failure_result('Invalid order status') unless valid_order_status?

    process_confirmation
  end

  private

  def process_confirmation
    update_order_status
    send_confirmation_email
    log_confirmation_activity
    success_result
  end

  def update_order_status
    order.update!(
      status: 'confirmed',
      confirmed_at: Time.current,
      confirmed_by: user&.id
    )
  end

  def send_confirmation_email
    return unless should_send_email?

    OrderMailer.confirmation(user).deliver_later
  end

  def should_send_email?
    order.customer_email.present? && 
    order.email_notifications_enabled? &&
    !order.confirmation_email_sent?
  end

  def log_confirmation_activity
    ActivityLogger.log(
      action: 'order_confirmed',
      order_id: order.id,
      user_id: user&.id,
      timestamp: Time.current
    )
  end

  def valid_order_status?
    %w[pending processing].include?(order.status)
  end

  def current_admin_user
    User.find_by(role: 'admin', active: true)
  end

  def success_result
    {
      success: true,
      message: 'Order confirmation processed successfully',
      order_id: order.id
    }
  end

  def failure_result(message)
    {
      success: false,
      message: message,
      order_id: order&.id
    }
  end
end