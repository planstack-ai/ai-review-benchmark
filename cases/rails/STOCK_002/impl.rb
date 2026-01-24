# frozen_string_literal: true

class NonAtomicStockUpdateService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Race condition between stock check and update
    if product.stock > 0; product.update(stock: product.stock - 1); end
  end

  private

  def buggy_implementation
    # 実装
  end
end
