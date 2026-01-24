# frozen_string_literal: true

class ProcessPaymentService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: 円単位のままAPIに送信している。銭単位に変換すべき
    transaction_id = PaymentGateway.charge(@order.total)  # 1000円が1000銭（10円）として処理される

    @order.record_payment(transaction_id)
  end
end
