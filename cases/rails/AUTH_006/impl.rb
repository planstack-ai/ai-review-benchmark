# frozen_string_literal: true

class AccessOtherPointsService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Can access other user's points via API
    User.find(params[:user_id]).points
  end

  private

  def buggy_implementation
    # 実装
  end
end
