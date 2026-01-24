# frozen_string_literal: true

class StandardValidationService
  def initialize(order)
    @order = order
  end

  def execute
    # 正しい実装
    validates presence, format, numericality
  end

  private

  def process_order
    # 実装
  end
end
