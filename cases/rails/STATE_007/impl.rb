# frozen_string_literal: true

class DeliveryStatusRegressionService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Delivered can regress to shipping status
    update(delivery_status: new_status)
  end

  private

  def buggy_implementation
    # 実装
  end
end
