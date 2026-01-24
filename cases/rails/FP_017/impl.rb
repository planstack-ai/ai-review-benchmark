# frozen_string_literal: true

class OptimizedBatchInsertService
  def initialize(order)
    @order = order
  end

  def execute
    # 正しい実装
    insert_all with proper duplicate handling
  end

  private

  def process_order
    # 実装
  end
end
