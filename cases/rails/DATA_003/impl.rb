# frozen_string_literal: true

class OptimisticLockMissingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: No optimistic locking - last write wins silently
    update without version check
  end

  private

  def buggy_implementation
    # 実装
  end
end
