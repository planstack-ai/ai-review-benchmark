# frozen_string_literal: true

class AdminPermissionMissingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Regular users can change prices - admin check missing
    update_price
  end

  private

  def buggy_implementation
    # 実装
  end
end
