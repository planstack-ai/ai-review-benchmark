# frozen_string_literal: true

class ScopeNotUsedService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Scope not used - reimplementing where(status: 'active') everywhere
    Product.where(status: 'active')
  end

  private

  def buggy_implementation
    # 実装
  end
end
