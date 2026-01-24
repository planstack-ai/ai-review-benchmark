# frozen_string_literal: true

class PluckVsSelectService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: select loads full objects when only attributes needed
    Order.select(:id, :total).map { |o| [o.id, o.total] }
  end

  private

  def buggy_implementation
    # 実装
  end
end
