# frozen_string_literal: true

class InconsistentRoundingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Inconsistent rounding - round per item then sum vs sum then round yields different results
    items.sum { |i| i.subtotal.round }
  end

  private

  def buggy_implementation
    # 実装
  end
end
