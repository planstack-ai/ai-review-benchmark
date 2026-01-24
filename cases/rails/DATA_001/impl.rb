# frozen_string_literal: true

class NoForeignKeyService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: No foreign key constraint - orphan records on parent delete
    belongs_to :order without FK
  end

  private

  def buggy_implementation
    # 実装
  end
end
