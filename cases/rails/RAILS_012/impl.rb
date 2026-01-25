# frozen_string_literal: true

# Order payment processing service
# Handles charging customer and updating order status
class PaymentService
  def initialize(order)
    @order = order
  end

  def process_payment
    ActiveRecord::Base.transaction do
      order.update!(status: :processing)
      result = PaymentGateway.charge(order.total)

      if result.success?
        order.update!(status: :paid, payment_ref: result.id)
      else
        raise ActiveRecord::Rollback
      end
    end

    order.paid?
  rescue PaymentGateway::PaymentError => e
    Rails.logger.error("Payment failed for order #{order.id}: #{e.message}")
    order.update(status: :failed)
    false
  end

  private

  attr_reader :order
end
