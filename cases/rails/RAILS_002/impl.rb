# frozen_string_literal: true

class OrderProcessingService
  class ProcessingError < StandardError; end

  def initialize(order)
    @order = order
    @notification_service = NotificationService.new
    @inventory_service = InventoryService.new
  end

  def process_order
    return false unless can_process_order?

    ActiveRecord::Base.transaction do
      validate_inventory_availability
      reserve_inventory_items
      calculate_final_pricing
      update_order_status
      send_confirmation_notifications
    end

    true
  rescue ProcessingError => e
    Rails.logger.error "Order processing failed: #{e.message}"
    false
  end

  def can_process_order?
    return false unless @order.present?
    return false if @order.status == 'cancelled'
    return false if @order.status == 'completed'
    
    @order.status == 'pending' && @order.items.any? && payment_valid?
  end

  def estimate_processing_time
    base_time = 2.hours
    
    if @order.status == 'pending'
      item_count = @order.items.count
      complexity_multiplier = calculate_complexity_multiplier(item_count)
      
      (base_time * complexity_multiplier).to_i
    else
      0
    end
  end

  private

  def validate_inventory_availability
    @order.items.each do |item|
      unless @inventory_service.available?(item.product_id, item.quantity)
        raise ProcessingError, "Insufficient inventory for product #{item.product_id}"
      end
    end
  end

  def reserve_inventory_items
    @order.items.each do |item|
      @inventory_service.reserve(item.product_id, item.quantity, @order.id)
    end
  end

  def calculate_final_pricing
    subtotal = @order.items.sum { |item| item.price * item.quantity }
    tax_amount = subtotal * tax_rate
    shipping_cost = calculate_shipping_cost
    
    @order.update!(
      subtotal: subtotal,
      tax_amount: tax_amount,
      shipping_cost: shipping_cost,
      total_amount: subtotal + tax_amount + shipping_cost
    )
  end

  def update_order_status
    @order.update!(status: 'processing', processed_at: Time.current)
  end

  def send_confirmation_notifications
    @notification_service.send_order_confirmation(@order)
    @notification_service.send_internal_notification(@order)
  end

  def payment_valid?
    @order.payment_method.present? && @order.payment_status == 'authorized'
  end

  def calculate_complexity_multiplier(item_count)
    case item_count
    when 1..5
      1.0
    when 6..15
      1.5
    else
      2.0
    end
  end

  def tax_rate
    @order.shipping_address&.tax_rate || 0.08
  end

  def calculate_shipping_cost
    return 0 if @order.total_weight < 1.0
    
    base_shipping = 9.99
    weight_surcharge = (@order.total_weight - 1.0) * 2.50
    
    base_shipping + weight_surcharge
  end
end