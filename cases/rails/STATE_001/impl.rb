# frozen_string_literal: true

class InvalidStateTransitionService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Invalid transition allowed - shipped can go back to pending
    update(status: new_status)
  end

  private

  def buggy_implementation
    # 実装
  end
end
