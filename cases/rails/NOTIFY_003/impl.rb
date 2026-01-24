# frozen_string_literal: true

class NotificationTimingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Order complete email sent before payment confirmation
    send_confirmation on order_create
  end

  private

  def buggy_implementation
    # 実装
  end
end
