# frozen_string_literal: true

class CancelWindowMissingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Cancellation succeeds even after shipment
    cancel!
  end

  private

  def buggy_implementation
    # 実装
  end
end
