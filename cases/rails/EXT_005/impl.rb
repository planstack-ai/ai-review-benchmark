# frozen_string_literal: true

class InventorySyncDelayService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: External warehouse stock diff not considered
    available = local_stock
  end

  private

  def buggy_implementation
    # 実装
  end
end
