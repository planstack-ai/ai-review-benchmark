# frozen_string_literal: true

class TransactionNestingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Nested transaction without requires_new rolls back parent
    transaction { transaction { ... } }
  end

  private

  def buggy_implementation
    # 実装
  end
end
