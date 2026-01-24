# frozen_string_literal: true

class WebhookNotIdempotentService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Same webhook processed multiple times
    process
  end

  private

  def buggy_implementation
    # 実装
  end
end
