# frozen_string_literal: true

class FloatingPointCurrencyService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Floating point precision error - 0.1 + 0.2 != 0.3 problem
    0.1 + 0.2
  end

  private

  def buggy_implementation
    # 実装
  end
end
