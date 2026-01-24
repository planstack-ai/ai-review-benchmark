# frozen_string_literal: true

class IntentionalEagerLoadService
  def initialize(order)
    @order = order
  end

  def execute
    # 正しい実装
    Extra includes for downstream use
  end

  private

  def process_order
    # 実装
  end
end
