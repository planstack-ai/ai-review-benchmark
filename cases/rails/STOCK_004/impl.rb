# frozen_string_literal: true

class ReservedActualConfusionService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Reserved stock counted as available - double counting
    available = total_stock
  end

  private

  def buggy_implementation
    # 実装
  end
end
