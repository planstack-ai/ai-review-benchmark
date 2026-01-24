# frozen_string_literal: true

class RecipientMixupService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Email sent to wrong user due to variable scope
    OrderMailer.confirmation(user).deliver_later
  end

  private

  def buggy_implementation
    # 実装
  end
end
