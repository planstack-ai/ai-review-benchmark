# frozen_string_literal: true

class ShippingErrorSwallowedService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Shipping API error swallowed, treated as success
    response rescue nil
  end

  private

  def buggy_implementation
    # 実装
  end
end
