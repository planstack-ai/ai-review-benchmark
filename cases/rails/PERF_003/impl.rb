# frozen_string_literal: true

class UnnecessaryEagerLoadingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Eager loading unused associations wastes resources
    orders.includes(:items, :payments, :shipments, :user)
  end

  private

  def buggy_implementation
    # 実装
  end
end
