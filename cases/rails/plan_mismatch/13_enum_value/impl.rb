# frozen_string_literal: true

class OrderStatusService
  class InvalidTransitionError < StandardError; end

  def initialize(order)
    @order = order
  end

  def advance_status
    case @order.status
    when "pending"
      # BUG: confirmed は存在しない。正しくは paid
      @order.confirmed!
    when "paid"
      @order.shipped!
    when "shipped"
      @order.delivered!
    else
      raise InvalidTransitionError, "Cannot advance from #{@order.status}"
    end
  end
end
