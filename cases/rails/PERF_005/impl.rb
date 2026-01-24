# frozen_string_literal: true

class IndexNotUsedService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Search condition on non-indexed column causes full scan
    query without index
  end

  private

  def buggy_implementation
    # 実装
  end
end
