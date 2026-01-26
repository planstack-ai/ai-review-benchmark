# frozen_string_literal: true

class OrderProcessingService
  class ProcessingError < StandardError; end

  def initialize(order)
    @order = order
  end

  def process_order
    ActiveRecord::Base.transaction do
      validate_order_requirements
      reserve_inventory_items

      ActiveRecord::Base.transaction(requires_new: true) do
        update_order_status

        ActiveRecord::Base.transaction(requires_new: true) do
          update_inventory_logs
        end
      end
    end

    @order.reload
  rescue ActiveRecord::RecordInvalid => e
    handle_validation_error(e)
  rescue InsufficientStockError => e
    handle_stock_error(e)
  rescue ProcessingError => e
    handle_processing_error(e)
  end

  private

  def validate_order_requirements
    raise ProcessingError, "Order already confirmed" if @order.status == 'confirmed'
    raise ProcessingError, "Invalid order total" unless @order.total_amount > 0
    raise ProcessingError, "No items in order" if @order.order_items.empty?
  end

  def reserve_inventory_items
    @order.order_items.each do |item|
      product = item.product
      raise InsufficientStockError, "Insufficient stock for #{product.name}" unless product.available?(item.quantity)
    end
  end

  def update_order_status
    @order.update!(status: 'confirmed')
  end

  def update_inventory_logs
    @order.order_items.each do |item|
      item.product.reserve_stock!(item.quantity, 'order_confirmed')
    end
  end

  def handle_validation_error(error)
    Rails.logger.error "Order validation failed: #{error.message}"
    raise ProcessingError, "Order validation failed"
  end

  def handle_stock_error(error)
    Rails.logger.error "Inventory error: #{error.message}"
    raise ProcessingError, "Insufficient inventory"
  end

  def handle_processing_error(error)
    Rails.logger.error "Order processing failed: #{error.message}"
    @order.update(status: 'cancelled') if @order.persisted?
    raise error
  end
end
