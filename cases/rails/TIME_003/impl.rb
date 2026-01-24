# frozen_string_literal: true

class CouponExpiryComparisonService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Off-by-one on expiry - using < instead of <=
    Time.current < expires_at
  end

  private

  def buggy_implementation
    # 実装
  end
end
