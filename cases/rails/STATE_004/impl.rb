# frozen_string_literal: true

class DuplicatePaymentService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Double-click charges twice - no duplicate check
    process_payment
  end

  private

  def buggy_implementation
    # 実装
  end
end
