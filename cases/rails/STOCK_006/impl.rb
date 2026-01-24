# frozen_string_literal: true

class NegativeStockAllowedService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Cancellation processing can drive stock negative
    stock += cancelled_qty
  end

  private

  def buggy_implementation
    # 実装
  end
end
