# frozen_string_literal: true

class DiscountService
  PREMIUM_DISCOUNT_RATE = 0.9  # 10%割引 = 支払い率90%

  def initialize(order)
    @order = order
  end

  def apply
    return unless @order.user.premium?

    @order.apply_discount(PREMIUM_DISCOUNT_RATE)
    @order.save!
  end
end
