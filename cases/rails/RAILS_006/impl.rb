# frozen_string_literal: true

class StrongParametersMissingService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Strong Parameters missing - mass assignment vulnerability
    params[:order]
  end

  private

  def buggy_implementation
    # 実装
  end
end
