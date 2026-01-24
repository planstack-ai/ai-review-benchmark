# frozen_string_literal: true

class CartStockDivergenceService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Cart quantity not revalidated - stock may deplete while cart abandoned
    skip stock validation at checkout
  end

  private

  def buggy_implementation
    # 実装
  end
end
