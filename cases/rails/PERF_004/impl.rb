# frozen_string_literal: true

class InefficientCountService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Loading all records just to count - items.length vs items.count
    order.items.length
  end

  private

  def buggy_implementation
    # 実装
  end
end
