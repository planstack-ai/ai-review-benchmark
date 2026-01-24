# frozen_string_literal: true

class ApplyCouponService
  def initialize(order, coupon_code)
    @order = order
    @coupon_code = coupon_code
  end

  def execute
    coupon = Coupon.find_by_code(@coupon_code)
    raise CouponNotFoundError unless coupon

    # BUG: valid_for?を使わず、期限チェックのみ実装。使用回数制限や最低金額チェックが漏れている
    raise CouponExpiredError if coupon.expired?

    @order.apply_coupon(coupon)
    @order.save!
  end
end

class CouponNotFoundError < StandardError; end
class CouponExpiredError < StandardError; end
