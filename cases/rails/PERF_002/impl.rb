# frozen_string_literal: true

class FullTableLoadService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Loading all orders into memory - Order.all on 1M records
    Order.all.each { |o| process(o) }
  end

  private

  def buggy_implementation
    # 実装
  end
end
