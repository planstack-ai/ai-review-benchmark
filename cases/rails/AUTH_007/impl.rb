# frozen_string_literal: true

class CouponOwnerMissingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Can use another user's coupon code
    Coupon.find_by(code: code)
  end

  private

  def buggy_implementation
    # 実装
  end
end
