# frozen_string_literal: true

class CouponStackingLogicService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Coupon stacking allowed - multiple coupons can be applied
    apply_coupon(coupon)
  end

  private

  def buggy_implementation
    # 実装
  end
end
