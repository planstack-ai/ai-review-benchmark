# frozen_string_literal: true

class OrderCancellationService
  class CannotCancelError < StandardError; end
  class OrderNotFoundError < StandardError; end

  def initialize(order_id, user_id, reason = nil)
    @order_id = order_id
    @user_id = user_id
    @reason = reason || 'Customer requested cancellation'
  end

  def call
    validate_order_exists!
    validate_user_authorization!
    validate_order_status!
    
    process_cancellation
    notify_stakeholders
    
    { success: true, message: 'Order cancelled successfully' }
  rescue CannotCancelError, OrderNotFoundError => e
    { success: false, error: e.message }
  end

  private

  attr_reader :order_id, :user_id, :reason

  def order
    @order ||= Order.find_by(id: order_id)
  end

  def validate_order_exists!
    raise OrderNotFoundError, 'Order not found' unless order
  end

  def validate_user_authorization!
    unless user_can_cancel_order?
      raise CannotCancelError, 'User not authorized to cancel this order'
    end
  end

  def validate_order_status!
    if order.cancelled?
      raise CannotCancelError, 'Order is already cancelled'
    end
    
    if order.completed?
      raise CannotCancelError, 'Cannot cancel completed order'
    end
  end

  def user_can_cancel_order?
    order.user_id == user_id || User.find(user_id)&.admin?
  end

  def process_cancellation
    ActiveRecord::Base.transaction do
      order.cancel!
      create_cancellation_record
      process_refund if payment_processed?
      release_inventory
    end
  end

  def create_cancellation_record
    OrderCancellation.create!(
      order: order,
      user_id: user_id,
      reason: reason,
      cancelled_at: Time.current
    )
  end

  def payment_processed?
    order.payment_status == 'paid' || order.payment_status == 'authorized'
  end

  def process_refund
    RefundService.new(order).process_automatic_refund
  end

  def release_inventory
    order.order_items.each do |item|
      InventoryService.new(item.product).release_reserved_quantity(item.quantity)
    end
  end

  def notify_stakeholders
    OrderMailer.cancellation_confirmation(order).deliver_later
    NotificationService.new(order).send_cancellation_alerts
  end
end