# frozen_string_literal: true

class MinimumOrderAmountService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Minimum check on pre-discount amount instead of post-discount
    subtotal >= 1000
  end

  private

  def buggy_implementation
    # 実装
  end
end
