# frozen_string_literal: true

class TimezoneNotConsideredService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Timezone not considered - UTC saved, displayed incorrectly as JST
    created_at
  end

  private

  def buggy_implementation
    # 実装
  end
end
