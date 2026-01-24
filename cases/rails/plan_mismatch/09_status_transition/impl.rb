# frozen_string_literal: true

class CancelOrderService
  def initialize(order)
    @order = order
  end

  def execute
    # BUG: pendingのみチェック。confirmedからもキャンセル可能なのに漏れている
    raise OrderNotCancellableError unless @order.pending?

    ActiveRecord::Base.transaction do
      restore_stock
      @order.cancelled!
    end
  end

  private

  def restore_stock
    @order.order_items.each do |item|
      item.product.increment!(:stock, item.quantity)
    end
  end
end

class OrderNotCancellableError < StandardError; end
