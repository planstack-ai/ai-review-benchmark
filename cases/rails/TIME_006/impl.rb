# frozen_string_literal: true

class YearCrossingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Year crossing logic error - 12/31 to 1/1 fails
    Date.new(year, month, day + 1)
  end

  private

  def buggy_implementation
    # 実装
  end
end
