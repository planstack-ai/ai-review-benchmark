# frozen_string_literal: true

class FreeShippingBoundaryService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Boundary condition error - >= 5000 vs > 5000
    total > 5000 ? 0 : shipping_fee
  end

  private

  def buggy_implementation
    # 実装
  end
end
