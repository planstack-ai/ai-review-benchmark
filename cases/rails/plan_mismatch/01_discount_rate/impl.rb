# frozen_string_literal: true

class CheckoutService
  def initialize(order)
    @order = order
  end

  def execute
    apply_member_discount if @order.user.member?
    process_payment
    confirm_order
  end

  private

  def apply_member_discount
    # 会員には10%割引を適用
    @order.total *= 0.1  # BUG: 0.9であるべき（10%割引 = 90%支払い）
    @order.save!
  end

  def process_payment
    PaymentGateway.charge(@order.total)
  end

  def confirm_order
    @order.confirmed!
  end
end
