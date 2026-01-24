# frozen_string_literal: true

class WebhookProcessorService
  attr_reader :event_id, :event_type, :payload

  def initialize(event_id:, event_type:, payload:)
    @event_id = event_id
    @event_type = event_type
    @payload = payload
  end

  def call
    return failure_result("Invalid event type") unless valid_event_type?
    return failure_result("Missing required payload data") unless valid_payload?

    process_webhook_event
    log_webhook_processing
    
    success_result
  rescue StandardError => e
    Rails.logger.error "Webhook processing failed: #{e.message}"
    failure_result("Processing failed: #{e.message}")
  end

  private

  def valid_event_type?
    %w[user.created user.updated user.deleted order.completed payment.processed].include?(event_type)
  end

  def valid_payload?
    payload.is_a?(Hash) && payload.key?('id') && payload.key?('timestamp')
  end

  def process_webhook_event
    case event_type
    when 'user.created'
      create_user_from_webhook
    when 'user.updated'
      update_user_from_webhook
    when 'user.deleted'
      delete_user_from_webhook
    when 'order.completed'
      process_order_completion
    when 'payment.processed'
      process_payment_completion
    end
  end

  def create_user_from_webhook
    User.create!(
      external_id: payload['id'],
      email: payload['email'],
      name: payload['name'],
      created_at: Time.parse(payload['timestamp'])
    )
  end

  def update_user_from_webhook
    user = User.find_by(external_id: payload['id'])
    return unless user

    user.update!(
      email: payload['email'],
      name: payload['name']
    )
  end

  def delete_user_from_webhook
    user = User.find_by(external_id: payload['id'])
    user&.destroy
  end

  def process_order_completion
    order = Order.find_by(external_id: payload['id'])
    return unless order

    order.update!(status: 'completed', completed_at: Time.parse(payload['timestamp']))
    OrderMailer.completion_notification(order).deliver_later
  end

  def process_payment_completion
    payment = Payment.find_by(external_id: payload['id'])
    return unless payment

    payment.update!(
      status: 'processed',
      processed_at: Time.parse(payload['timestamp']),
      amount: payload['amount']
    )
  end

  def log_webhook_processing
    WebhookLog.create!(
      event_id: event_id,
      event_type: event_type,
      payload: payload,
      processed_at: Time.current,
      status: 'success'
    )
  end

  def success_result
    { success: true, message: "Webhook processed successfully" }
  end

  def failure_result(message)
    { success: false, message: message }
  end
end