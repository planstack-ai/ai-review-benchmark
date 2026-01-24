# frozen_string_literal: true

class PaymentProcessingService
  include ActiveModel::Model

  attr_accessor :order, :payment_method, :amount

  def initialize(order:, payment_method:, amount:)
    @order = order
    @payment_method = payment_method
    @amount = amount
    @payment_gateway = PaymentGateway.new
  end

  def call
    return failure_result('Invalid order') unless valid_order?
    return failure_result('Invalid payment method') unless valid_payment_method?
    return failure_result('Invalid amount') unless valid_amount?

    process_payment_transaction
  end

  private

  def valid_order?
    order.present? && order.persisted? && order.pending?
  end

  def valid_payment_method?
    payment_method.present? && payment_method.active?
  end

  def valid_amount?
    amount.present? && amount.positive? && amount == order.total_amount
  end

  def process_payment_transaction
    ActiveRecord::Base.transaction do
      payment_result = process_payment
      
      if payment_result.success?
        order.update!(status: 'paid', paid_at: Time.current)
        create_payment_record(payment_result)
        send_confirmation_email
        success_result(payment_result)
      else
        failure_result(payment_result.error_message)
      end
    end
  rescue StandardError => e
    Rails.logger.error "Payment processing failed: #{e.message}"
    failure_result('Payment processing failed')
  end

  def process_payment
    @payment_gateway.charge(
      amount: amount,
      payment_method: payment_method,
      order_id: order.id,
      description: "Payment for order ##{order.number}"
    )
  end

  def expired?
    order.expires_at.present? && order.expires_at < Time.current
  end

  def create_payment_record(payment_result)
    Payment.create!(
      order: order,
      payment_method: payment_method,
      amount: amount,
      gateway_transaction_id: payment_result.transaction_id,
      status: 'completed'
    )
  end

  def send_confirmation_email
    PaymentMailer.payment_confirmation(order).deliver_later
  end

  def success_result(payment_result)
    OpenStruct.new(
      success?: true,
      payment: payment_result,
      message: 'Payment processed successfully'
    )
  end

  def failure_result(message)
    OpenStruct.new(
      success?: false,
      error: message,
      message: message
    )
  end
end