# frozen_string_literal: true

class OrderConfirmationService
  attr_reader :order, :user, :email_service

  def initialize(order, email_service: EmailService.new)
    @order = order
    @user = order.user
    @email_service = email_service
    @max_retries = 3
    @retry_count = 0
  end

  def call
    return failure_result('Order not found') unless order
    return failure_result('User not found') unless user
    return success_result('Email already sent') if email_already_sent?

    send_confirmation_email_with_retry
  end

  private

  def send_confirmation_email_with_retry
    begin
      send_confirmation_email
      mark_email_as_sent
      success_result('Confirmation email sent successfully')
    rescue EmailDeliveryError => e
      handle_email_failure(e)
    rescue StandardError => e
      Rails.logger.error "Unexpected error in OrderConfirmationService: #{e.message}"
      failure_result('An unexpected error occurred')
    end
  end

  def send_confirmation_email
    email_service.send_order_confirmation(
      to: user.email,
      order_id: order.id,
      order_total: order.total_amount,
      items: order.line_items.includes(:product)
    )
  end

  def handle_email_failure(error)
    @retry_count += 1
    Rails.logger.warn "Email delivery failed (attempt #{@retry_count}): #{error.message}"
    
    if @retry_count < @max_retries
      sleep(exponential_backoff_delay)
      send_confirmation_email
      mark_email_as_sent
      success_result('Confirmation email sent after retry')
    else
      Rails.logger.error "Failed to send confirmation email after #{@max_retries} attempts"
      failure_result('Failed to send confirmation email')
    end
  end

  def exponential_backoff_delay
    (2 ** @retry_count) + rand(1..3)
  end

  def email_already_sent?
    order.confirmation_email_sent_at.present?
  end

  def mark_email_as_sent
    order.update!(confirmation_email_sent_at: Time.current)
  end

  def success_result(message)
    { success: true, message: message }
  end

  def failure_result(message)
    { success: false, message: message }
  end
end