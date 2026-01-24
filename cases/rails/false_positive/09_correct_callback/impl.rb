# frozen_string_literal: true

class OrderConfirmationService
  def initialize(order)
    @order = order
  end

  def execute
    return false unless @order.pending?

    @order.confirm!
    true
  end
end
