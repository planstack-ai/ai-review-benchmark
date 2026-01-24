# frozen_string_literal: true

class StandardScopeService
  def initialize(order)
    @order = order
  end

  def execute
    # 正しい実装
    scope :active, -> { where(active: true) }
  end

  private

  def process_order
    # 実装
  end
end
