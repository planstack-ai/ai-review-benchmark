# frozen_string_literal: true

class PartialCancelIntegrityService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Total amount wrong after partial item cancellation
    partial_cancel without recalculation
  end

  private

  def buggy_implementation
    # 実装
  end
end
