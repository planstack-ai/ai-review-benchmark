# frozen_string_literal: true

class OrderCancellationService
  attr_reader :order, :items_to_cancel, :cancellation_reason

  def initialize(order, items_to_cancel, cancellation_reason = nil)
    @order = order
    @items_to_cancel = items_to_cancel
    @cancellation_reason = cancellation_reason
  end

  def call
    return failure_result('Order not found') unless order
    return failure_result('No items to cancel') if items_to_cancel.empty?
    return failure_result('Order already cancelled') if order.cancelled?

    ActiveRecord::Base.transaction do
      process_partial_cancellation
      update_order_status
      create_cancellation_record
      notify_stakeholders
    end

    success_result
  rescue StandardError => e
    failure_result("Cancellation failed: #{e.message}")
  end

  private

  def process_partial_cancellation
    items_to_cancel.each do |item_data|
      order_item = find_order_item(item_data[:id])
      next unless order_item

      cancel_quantity = [item_data[:quantity], order_item.quantity].min
      
      if cancel_quantity == order_item.quantity
        order_item.update!(status: 'cancelled')
      else
        order_item.update!(
          quantity: order_item.quantity - cancel_quantity,
          status: 'partially_cancelled'
        )
      end

      create_cancelled_item_record(order_item, cancel_quantity)
    end
  end

  def find_order_item(item_id)
    order.order_items.find_by(id: item_id)
  end

  def create_cancelled_item_record(order_item, cancelled_quantity)
    order.cancelled_items.create!(
      original_order_item_id: order_item.id,
      product_id: order_item.product_id,
      quantity: cancelled_quantity,
      unit_price: order_item.unit_price,
      reason: cancellation_reason
    )
  end

  def update_order_status
    remaining_items = order.order_items.where.not(status: 'cancelled')
    
    if remaining_items.empty?
      order.update!(status: 'cancelled', cancelled_at: Time.current)
    else
      order.update!(status: 'partially_cancelled', updated_at: Time.current)
    end
  end

  def create_cancellation_record
    order.cancellation_logs.create!(
      items_cancelled: items_to_cancel.size,
      reason: cancellation_reason,
      processed_at: Time.current,
      processed_by: current_user_id
    )
  end

  def notify_stakeholders
    OrderCancellationMailer.partial_cancellation_notice(order).deliver_later
    WebhookService.new(order, 'order.partially_cancelled').call
  end

  def current_user_id
    Current.user&.id
  end

  def success_result
    { success: true, order: order.reload }
  end

  def failure_result(message)
    { success: false, error: message }
  end
end