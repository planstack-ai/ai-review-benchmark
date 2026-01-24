# frozen_string_literal: true

class AddToCartService
  def initialize(cart, product, quantity)
    @cart = cart
    @product = product
    @quantity = quantity
  end

  def execute
    cart_item = CartItem.find_or_initialize_by(cart: @cart, product: @product)
    cart_item.quantity ||= 0
    cart_item.quantity += @quantity
    # BUG: 数量上限チェックがない。quantity_exceeded?で確認すべき
    cart_item.save!
    cart_item
  end
end
