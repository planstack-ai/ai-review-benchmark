# frozen_string_literal: true

class CallbackOrderDependencyService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: before_save callback order affects result
    assume callback order
  end

  private

  def buggy_implementation
    # 実装
  end
end
