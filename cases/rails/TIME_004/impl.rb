# frozen_string_literal: true

class DateOnlyComparisonService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Time truncation causes next-day treatment
    delivery_date == target_date
  end

  private

  def buggy_implementation
    # 実装
  end
end
