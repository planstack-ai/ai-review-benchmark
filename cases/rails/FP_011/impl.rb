# frozen_string_literal: true

class IntentionalNoValidationService
  def initialize(order)
    @order = order
  end

  def execute
    # 正しい実装
    Intentional skip_validation for admin
  end

  private

  def process_order
    # 実装
  end
end
