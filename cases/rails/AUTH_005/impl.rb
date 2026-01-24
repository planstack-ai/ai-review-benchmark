# frozen_string_literal: true

class GuestMemberPricingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Guest users getting member pricing - membership check hole
    member_price
  end

  private

  def buggy_implementation
    # 実装
  end
end
