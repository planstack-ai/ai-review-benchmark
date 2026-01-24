# frozen_string_literal: true

class DuplicateEmailService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Retry logic sends duplicate confirmation emails
    send_email
  end

  private

  def buggy_implementation
    # 実装
  end
end
