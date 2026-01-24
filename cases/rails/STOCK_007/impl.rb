# frozen_string_literal: true

class OrderCancellationService
  attr_reader :order, :cancellation_reason, :user

  def initialize(order, cancellation_reason: nil, user: nil)
    @order = order
    @cancellation_reason = cancellation_reason
    @user = user
  end

  def call
    return failure_result('Order cannot be cancelled') unless cancellable?

    ActiveRecord::Base.transaction do
      cancel_order
      restore_inventory_stock
      process_refund if refundable?
      notify_stakeholders
      log_cancellation_activity
    end

    success_result
  rescue StandardError => e
    failure_result("Cancellation failed: #{e.message}")
  end

  private

  def cancellable?
    order.pending? || order.confirmed?
  end

  def cancel_order
    order.update!(
      status: 'cancelled',
      cancelled_at: Time.current,
      cancellation_reason: cancellation_reason
    )
  end

  def restore_inventory_stock
    order.order_items.includes(:product).each do |order_item|
      restore_stock_for_item(order_item)
    end
  end

  def restore_stock_for_item(order_item)
    product = order_item.product
    quantity = order_item.quantity

    product.with_lock do
      product.update!(stock_quantity: product.stock_quantity + quantity)
    end

    StockMovement.create!(
      product: product,
      quantity: quantity,
      movement_type: 'restoration',
      reference: order,
      created_by: user
    )
  end

  def refundable?
    order.payment_status == 'paid'
  end

  def process_refund
    RefundService.new(order, user: user).call
  end

  def notify_stakeholders
    OrderMailer.cancellation_notification(order).deliver_later
    
    if order.total_amount > 500
      AdminNotificationService.new(
        type: 'high_value_cancellation',
        order: order,
        user: user
      ).call
    end
  end

  def log_cancellation_activity
    ActivityLog.create!(
      trackable: order,
      action: 'cancelled',
      user: user,
      metadata: {
        reason: cancellation_reason,
        cancelled_at: order.cancelled_at,
        total_amount: order.total_amount
      }
    )
  end

  def success_result
    { success: true, order: order }
  end

  def failure_result(message)
    { success: false, error: message }
  end
end