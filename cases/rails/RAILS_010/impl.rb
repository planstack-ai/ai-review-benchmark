# frozen_string_literal: true

class IncludesPreloadEagerLoadService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Wrong eager loading method generates unexpected query
    orders.includes(:items).where(items: { ... })
  end

  private

  def buggy_implementation
    # 実装
  end
end
