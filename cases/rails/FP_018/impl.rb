# frozen_string_literal: true

class OptimizedCacheWarmingService
  def initialize(order)
    @order = order
  end

  def execute
    # 正しい実装
    Intentional full table load into cache
  end

  private

  def process_order
    # 実装
  end
end
