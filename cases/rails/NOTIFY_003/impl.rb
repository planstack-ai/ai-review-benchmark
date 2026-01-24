# frozen_string_literal: true

class OrderProcessingService
  attr_reader :order, :payment_processor, :notification_service

  def initialize(order, payment_processor: PaymentProcessor.new, notification_service: NotificationService.new)
    @order = order
    @payment_processor = payment_processor
    @notification_service = notification_service
  end

  def process_order
    return failure_result('Order already processed') if order.processed?

    ActiveRecord::Base.transaction do
      update_order_status
      process_payment
      send_order_confirmation
      update_inventory
      log_order_completion
    end

    success_result
  rescue StandardError => e
    Rails.logger.error "Order processing failed for order #{order.id}: #{e.message}"
    failure_result(e.message)
  end

  private

  def update_order_status
    order.update!(status: 'processing', processed_at: Time.current)
  end

  def process_payment
    payment_result = payment_processor.charge(
      amount: order.total_amount,
      payment_method: order.payment_method,
      customer_id: order.customer_id
    )

    if payment_result.success?
      order.update!(
        payment_status: 'confirmed',
        payment_confirmed_at: Time.current,
        transaction_id: payment_result.transaction_id
      )
    else
      raise PaymentError, payment_result.error_message
    end
  end

  def send_order_confirmation
    notification_service.send_order_confirmation(
      customer_email: order.customer.email,
      order_details: order_confirmation_details
    )
  end

  def update_inventory
    order.line_items.each do |item|
      InventoryService.new(item.product).reduce_stock(item.quantity)
    end
  end

  def log_order_completion
    OrderActivityLogger.log(
      order_id: order.id,
      activity: 'order_completed',
      timestamp: Time.current
    )
  end

  def order_confirmation_details
    {
      order_number: order.number,
      total_amount: order.total_amount,
      items: order.line_items.map(&:summary),
      estimated_delivery: calculate_delivery_date
    }
  end

  def calculate_delivery_date
    business_days = order.shipping_method.delivery_days
    Date.current + business_days.business_days
  end

  def success_result
    { success: true, order_id: order.id }
  end

  def failure_result(message)
    { success: false, error: message }
  end
end