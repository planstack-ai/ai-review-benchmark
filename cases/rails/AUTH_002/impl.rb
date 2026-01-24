# frozen_string_literal: true

class ManipulateOtherCartService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Can manipulate other user's cart by specifying cart_id
    Cart.find(params[:cart_id]).add_item(item)
  end

  private

  def buggy_implementation
    # 実装
  end
end
