# frozen_string_literal: true

class BundleStockCalculationService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Bundle stock not calculated as minimum of components
    components.sum(&:stock)
  end

  private

  def buggy_implementation
    # 実装
  end
end
