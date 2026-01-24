# frozen_string_literal: true

class RefundStatusMissingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Payment shows unpaid despite refund completion
    process_refund without status update
  end

  private

  def buggy_implementation
    # 実装
  end
end
