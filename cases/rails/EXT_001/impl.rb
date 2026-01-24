# frozen_string_literal: true

class PaymentTimeoutUnhandledService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Payment timeout leaves order in unknown state
    rescue Timeout::Error => e; raise
  end

  private

  def buggy_implementation
    # 実装
  end
end
