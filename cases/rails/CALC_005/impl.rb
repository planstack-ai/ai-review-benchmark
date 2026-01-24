# frozen_string_literal: true

class HardcodedTaxRateService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Hardcoded old tax rate - still using 8% instead of 10%
    subtotal * 0.08
  end

  private

  def buggy_implementation
    # 実装
  end
end
