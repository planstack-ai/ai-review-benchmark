# frozen_string_literal: true

class MasterDataHistoryService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Product name change affects past order display
    order_item.product.name
  end

  private

  def buggy_implementation
    # 実装
  end
end
