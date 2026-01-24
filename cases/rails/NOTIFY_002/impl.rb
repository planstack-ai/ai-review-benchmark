# frozen_string_literal: true

class AsyncErrorSwallowedService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Background job fails silently - user not notified
    rescue => e; logger.error(e)
  end

  private

  def buggy_implementation
    # 実装
  end
end
