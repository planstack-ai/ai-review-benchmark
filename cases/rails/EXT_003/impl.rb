# frozen_string_literal: true

class ApiCallInTransactionService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Payment charged even if transaction rolls back
    transaction { order.save!; charge_payment }
  end

  private

  def buggy_implementation
    # 実装
  end
end
