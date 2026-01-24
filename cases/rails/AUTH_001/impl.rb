# frozen_string_literal: true

class AccessOtherUserOrderService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: IDOR vulnerability - can access other user's order by changing ID
    Order.find(params[:id])
  end

  private

  def buggy_implementation
    # 実装
  end
end
