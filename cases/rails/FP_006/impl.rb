# frozen_string_literal: true

class OrderProcessingService
  class ProcessingError < StandardError; end

  def initialize(order)
    @order = order
    @payment_processor = PaymentProcessor.new
    @inventory_manager = InventoryManager.new
    @notification_service = NotificationService.new
  end

  def process_order
    ActiveRecord::Base.transaction do
      validate_order_requirements
      reserve_inventory_items
      
      ActiveRecord::Base.transaction(requires_new: true) do
        process_payment_transaction
        update_order_status
        
        ActiveRecord::Base.transaction do
          create_shipment_record
          update_customer_loyalty_points
          schedule_fulfillment_tasks
        end
      end
      
      send_confirmation_notifications
    end
    
    @order.reload
  rescue ActiveRecord::RecordInvalid => e
    handle_validation_error(e)
  rescue PaymentProcessor::PaymentError => e
    handle_payment_error(e)
  rescue ProcessingError => e
    handle_processing_error(e)
  end

  private

  def validate_order_requirements
    raise ProcessingError, "Order already processed" if @order.processed?
    raise ProcessingError, "Invalid order total" unless @order.total > 0
    raise ProcessingError, "No items in order" if @order.order_items.empty?
  end

  def reserve_inventory_items
    @order.order_items.each do |item|
      unless @inventory_manager.reserve_item(item.product_id, item.quantity)
        raise ProcessingError, "Insufficient inventory for product #{item.product_id}"
      end
    end
  end

  def process_payment_transaction
    payment_result = @payment_processor.charge(
      amount: @order.total,
      payment_method: @order.payment_method,
      customer_id: @order.customer_id
    )
    
    @order.update!(
      payment_transaction_id: payment_result.transaction_id,
      payment_status: 'completed'
    )
  end

  def update_order_status
    @order.update!(
      status: 'processing',
      processed_at: Time.current
    )
  end

  def create_shipment_record
    shipment = Shipment.create!(
      order: @order,
      tracking_number: generate_tracking_number,
      estimated_delivery: calculate_delivery_date,
      shipping_address: @order.shipping_address
    )
    
    @order.update!(shipment: shipment)
  end

  def update_customer_loyalty_points
    points_earned = (@order.total * 0.01).to_i
    @order.customer.increment!(:loyalty_points, points_earned)
  end

  def schedule_fulfillment_tasks
    FulfillmentJob.perform_later(@order.id)
    InventoryUpdateJob.perform_later(@order.order_items.pluck(:product_id))
  end

  def send_confirmation_notifications
    @notification_service.send_order_confirmation(@order)
  end

  def generate_tracking_number
    "TRK#{Time.current.to_i}#{@order.id}"
  end

  def calculate_delivery_date
    business_days = @order.shipping_method == 'express' ? 2 : 5
    business_days.business_days.from_now
  end

  def handle_validation_error(error)
    Rails.logger.error "Order validation failed: #{error.message}"
    raise ProcessingError, "Order validation failed"
  end

  def handle_payment_error(error)
    Rails.logger.error "Payment processing failed: #{error.message}"
    @order.update(payment_status: 'failed')
    raise ProcessingError, "Payment processing failed"
  end

  def handle_processing_error(error)
    Rails.logger.error "Order processing failed: #{error.message}"
    @order.update(status: 'failed') if @order.persisted?
    raise error
  end
end