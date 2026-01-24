# frozen_string_literal: true

class StockUpdateService
  class InsufficientStockError < StandardError; end
  class ProductNotFoundError < StandardError; end

  def initialize(product_id, quantity = 1)
    @product_id = product_id
    @quantity = quantity
    @product = nil
  end

  def call
    validate_inputs
    load_product
    process_stock_update
    
    {
      success: true,
      product: @product,
      remaining_stock: @product.stock
    }
  rescue InsufficientStockError, ProductNotFoundError => e
    {
      success: false,
      error: e.message,
      product: @product
    }
  end

  private

  def validate_inputs
    raise ArgumentError, "Quantity must be positive" if @quantity <= 0
    raise ArgumentError, "Product ID cannot be nil" if @product_id.nil?
  end

  def load_product
    @product = Product.find_by(id: @product_id)
    raise ProductNotFoundError, "Product with ID #{@product_id} not found" unless @product
  end

  def process_stock_update
    check_stock_availability
    update_stock_level
    log_stock_change
  end

  def check_stock_availability
    if @product.stock < @quantity
      raise InsufficientStockError, "Insufficient stock. Available: #{@product.stock}, Requested: #{@quantity}"
    end
  end

  def update_stock_level
    new_stock_level = @product.stock - @quantity
    @product.update!(stock: new_stock_level)
  end

  def log_stock_change
    Rails.logger.info "Stock updated for product #{@product.id}: #{@product.stock + @quantity} -> #{@product.stock}"
  end
end