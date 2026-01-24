# frozen_string_literal: true

class ColumnDefaultNullService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: New column defaults to NULL causing downstream errors
    add_column :orders, :priority, :integer
  end

  private

  def buggy_implementation
    # 実装
  end
end
