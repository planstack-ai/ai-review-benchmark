# frozen_string_literal: true

class PaymentTimeoutService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Payment accepted after order expiration time
    process_payment
  end

  private

  def buggy_implementation
    # 実装
  end
end
