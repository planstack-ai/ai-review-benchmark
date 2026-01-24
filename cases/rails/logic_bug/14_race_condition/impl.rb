# frozen_string_literal: true

class ReservationService
  def initialize(product:, user:, quantity:)
    @product = product
    @user = user
    @quantity = quantity
  end

  def execute
    # BUG: Race condition - チェックと更新の間に別リクエストが割り込む可能性
    # 既存の reserve_stock! メソッドを使用すべき
    raise InsufficientStockError if @product.stock < @quantity

    @product.decrement!(:stock, @quantity)
    Reservation.create!(product: @product, user: @user, quantity: @quantity)
  end
end
