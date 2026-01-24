# frozen_string_literal: true

class OrderCancellationService
  CANCELLABLE_STATUSES = %w[pending confirmed].freeze

  def initialize(order)
    @order = order
  end

  def can_cancel?
    # BUG: 大文字小文字を考慮していない
    # "PENDING" や "Confirmed" などのケースで false を返してしまう
    CANCELLABLE_STATUSES.include?(@order.status)
  end

  def cancel!
    raise OrderNotCancellableError unless can_cancel?

    @order.update!(status: "cancelled")
    refund_payment
    notify_user
  end

  private

  def refund_payment
    PaymentService.refund(@order)
  end

  def notify_user
    OrderMailer.cancellation_confirmation(@order).deliver_later
  end
end
