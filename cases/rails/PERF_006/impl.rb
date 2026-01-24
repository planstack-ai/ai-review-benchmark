# frozen_string_literal: true

class CacheKeyDesignService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Same cache key for all users - cache collision
    Rails.cache.fetch('orders')
  end

  private

  def buggy_implementation
    # 実装
  end
end
