# frozen_string_literal: true

class StockAllocationTimingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Stock allocated at cart addition instead of payment confirmation
    reserve_stock on add_to_cart
  end

  private

  def buggy_implementation
    # 実装
  end
end
