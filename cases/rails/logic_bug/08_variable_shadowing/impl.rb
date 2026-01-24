# frozen_string_literal: true

class StockUpdateService
  def initialize(product, quantity)
    @product = product
    @quantity = quantity
  end

  def execute
    validate_stock!
    update_stock
  end

  private

  def validate_stock!
    # BUG: Local variable 'stock' shadows the method call intention
    # This creates a new local variable instead of getting product's stock
    stock = @product.stock
    raise InsufficientStockError if stock < @quantity
  end

  def update_stock
    # BUG: 'stock' here is undefined (different scope from validate_stock!)
    # Developer intended to use the value from validate_stock! but it's out of scope
    new_stock = stock - @quantity
    @product.update!(stock: new_stock)
    new_stock
  end
end
