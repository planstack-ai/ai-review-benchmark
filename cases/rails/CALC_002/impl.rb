# frozen_string_literal: true

class TaxCalculationOrderService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Tax calculation order wrong - applying tax before discount yields different amount
    (subtotal * 1.1) - discount
  end

  private

  def buggy_implementation
    # 実装
  end
end
