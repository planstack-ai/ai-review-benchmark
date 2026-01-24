# frozen_string_literal: true

class ComplexNestedTransactionService
  def initialize(order)
    @order = order
  end

  def execute
    # 正しい実装
    Nested transaction with requires_new: true
  end

  private

  def process_order
    # 実装
  end
end
