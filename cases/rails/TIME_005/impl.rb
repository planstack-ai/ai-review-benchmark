# frozen_string_literal: true

class MonthEndProcessingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Invalid date error - February 30 doesn't exist
    Date.new(year, month + 1, day)
  end

  private

  def buggy_implementation
    # 実装
  end
end
