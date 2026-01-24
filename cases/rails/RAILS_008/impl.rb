# frozen_string_literal: true

class UpdateAllSkipsCallbacksService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: update_all skips callbacks and validations
    orders.update_all(status: 'archived')
  end

  private

  def buggy_implementation
    # 実装
  end
end
