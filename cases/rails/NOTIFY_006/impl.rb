# frozen_string_literal: true

class BulkRateLimitService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Mass email send gets blocked by rate limit
    users.each { |u| send_email(u) }
  end

  private

  def buggy_implementation
    # 実装
  end
end
