# frozen_string_literal: true

class DeletedUserDataService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Deleted user's order data still accessible
    orders
  end

  private

  def buggy_implementation
    # 実装
  end
end
