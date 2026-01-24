# frozen_string_literal: true

class DuplicateStockRestorationService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Cancel spam increases stock - no idempotency check
    restore_stock
  end

  private

  def buggy_implementation
    # 実装
  end
end
