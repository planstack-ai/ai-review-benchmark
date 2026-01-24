# frozen_string_literal: true

class DiscountRateDirectionService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Discount rate direction wrong, becomes 90% off
    total * 0.1
  end

  private

  def buggy_implementation
    # 実装
  end
end
