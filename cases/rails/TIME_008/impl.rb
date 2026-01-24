# frozen_string_literal: true

class PastDeliveryDateService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: Past delivery dates accepted
    validates :delivery_date, presence: true
  end

  private

  def buggy_implementation
    # 実装
  end
end
