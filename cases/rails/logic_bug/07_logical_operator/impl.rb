# frozen_string_literal: true

class DiscountEligibilityService
  RECENT_PURCHASE_DAYS = 30
  DISCOUNT_RATE = 0.1

  def initialize(user)
    @user = user
  end

  def eligible?
    # BUG: || should be && (both conditions must be true)
    # This returns true if EITHER condition is met, not BOTH
    @user.premium? || @user.purchased_recently?(RECENT_PURCHASE_DAYS)
  end

  def apply_discount(amount)
    return amount unless eligible?

    amount * (1 - DISCOUNT_RATE)
  end
end
