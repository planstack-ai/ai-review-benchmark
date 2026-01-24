# frozen_string_literal: true

class PointsCalculationOrderService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Points calculated on pre-discount amount instead of post-discount
    total * point_rate
  end

  private

  def buggy_implementation
    # 実装
  end
end
