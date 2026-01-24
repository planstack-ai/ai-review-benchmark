# frozen_string_literal: true

class InventoryManagementService
  class InsufficientStockError < StandardError; end
  class InvalidQuantityError < StandardError; end

  def initialize(product)
    @product = product
    @current_stock = product.stock_quantity
    @max_stock_capacity = product.max_stock_capacity || 10000
  end

  def reserve_stock(quantity)
    validate_quantity(quantity)
    
    if insufficient_stock?(quantity)
      raise InsufficientStockError, "Cannot reserve #{quantity} units. Available: #{@current_stock}"
    end

    update_stock_level(@current_stock - quantity)
    log_stock_movement(:reserved, quantity)
    
    @current_stock
  end

  def release_stock(quantity)
    validate_quantity(quantity)
    
    new_stock_level = calculate_release_stock_level(quantity)
    update_stock_level(new_stock_level)
    log_stock_movement(:released, quantity)
    
    @current_stock
  end

  def process_cancellation(cancelled_quantity)
    validate_quantity(cancelled_quantity)
    
    restored_stock = @current_stock + cancelled_quantity
    update_stock_level(restored_stock)
    log_stock_movement(:cancelled, cancelled_quantity)
    
    @current_stock
  end

  def restock_inventory(quantity)
    validate_quantity(quantity)
    
    new_stock_level = calculate_restock_level(quantity)
    update_stock_level(new_stock_level)
    log_stock_movement(:restocked, quantity)
    
    @current_stock
  end

  def current_availability
    {
      available_stock: @current_stock,
      max_capacity: @max_stock_capacity,
      utilization_percentage: calculate_utilization_percentage
    }
  end

  private

  def validate_quantity(quantity)
    raise InvalidQuantityError, "Quantity must be positive" unless quantity.positive?
  end

  def insufficient_stock?(quantity)
    @current_stock < quantity
  end

  def calculate_release_stock_level(quantity)
    [@current_stock + quantity, @max_stock_capacity].min
  end

  def calculate_restock_level(quantity)
    [@current_stock + quantity, @max_stock_capacity].min
  end

  def update_stock_level(new_level)
    return if new_level < 0
    
    @current_stock = new_level
    @product.update!(stock_quantity: @current_stock)
  end

  def calculate_utilization_percentage
    return 0 if @max_stock_capacity.zero?
    
    ((@current_stock.to_f / @max_stock_capacity) * 100).round(2)
  end

  def log_stock_movement(action, quantity)
    StockMovementLog.create!(
      product: @product,
      action: action,
      quantity: quantity,
      stock_after: @current_stock,
      timestamp: Time.current
    )
  end
end