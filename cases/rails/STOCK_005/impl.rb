# frozen_string_literal: true

class ZeroQuantityOrderService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Zero quantity orders allowed through validation gap
    validates :quantity, numericality: { greater_than_or_equal_to: 0 }
  end

  private

  def buggy_implementation
    # 実装
  end
end
