# frozen_string_literal: true

class BusinessDayCalculationService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Weekends and holidays not excluded from business days
    3.days.from_now
  end

  private

  def buggy_implementation
    # 実装
  end
end
