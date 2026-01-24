# frozen_string_literal: true

class EnumNotUsedService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: String literal comparison instead of enum
    order.status == 'pending'
  end

  private

  def buggy_implementation
    # 実装
  end
end
