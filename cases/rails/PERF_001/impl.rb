# frozen_string_literal: true

class NPlusOneQueryService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: N+1 query on order items accessing product names
    order.items.each { |i| i.product.name }
  end

  private

  def buggy_implementation
    # 実装
  end
end
