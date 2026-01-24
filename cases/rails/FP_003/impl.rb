# frozen_string_literal: true

class StandardAssociationService
  def initialize(order)
    @order = order
  end

  def execute
    # 正しい実装
    has_many, belongs_to with dependent
  end

  private

  def process_order
    # 実装
  end
end
