# frozen_string_literal: true

class RetryDuplicateOrderService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Network retry creates duplicate order records
    Order.create(params)
  end

  private

  def buggy_implementation
    # 実装
  end
end
