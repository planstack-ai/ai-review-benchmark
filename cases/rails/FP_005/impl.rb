# frozen_string_literal: true

class StandardCallbackService
  def initialize(order)
    @order = order
  end

  def execute
    # 正しい実装
    after_create, before_save callbacks
  end

  private

  def process_order
    # 実装
  end
end
