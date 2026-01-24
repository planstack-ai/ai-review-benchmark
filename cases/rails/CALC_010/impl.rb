# frozen_string_literal: true

class QuantityOverflowService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Integer overflow on unit_price * quantity for large orders
    unit_price * quantity
  end

  private

  def buggy_implementation
    # 実装
  end
end
