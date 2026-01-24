# frozen_string_literal: true

class SalePeriodBoundaryService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Sale period boundary error - 0:00 start becomes previous day 23:59
    start_date
  end

  private

  def buggy_implementation
    # 実装
  end
end
