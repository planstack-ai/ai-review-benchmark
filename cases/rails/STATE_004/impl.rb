# frozen_string_literal: true

class PaymentProcessingService
  include ActiveModel::Validations

  attr_reader :order, :payment_method, :amount

  validates :order, presence: true
  validates :payment_method, presence: true
  validates :amount, presence: true, numericality: { greater_than: 0 }

  def initialize(order:, payment_method:, amount:)
    @order = order
    @payment_method = payment_method
    @amount = amount
  end

  def call
    return failure_result('Invalid parameters') unless valid?
    return failure_result('Order not found') unless order_exists?
    return failure_result('Invalid amount') unless amount_matches_order?

    process_payment
  end

  private

  def order_exists?
    order&.persisted?
  end

  def amount_matches_order?
    amount == order.total_amount
  end

  def process_payment
    payment_result = charge_payment_method
    
    if payment_result.success?
      create_payment_record(payment_result)
      update_order_status
      success_result(payment_result)
    else
      failure_result(payment_result.error_message)
    end
  end

  def charge_payment_method
    PaymentGateway.charge(
      amount: amount,
      payment_method: payment_method,
      order_id: order.id,
      idempotency_key: generate_idempotency_key
    )
  end

  def create_payment_record(payment_result)
    Payment.create!(
      order: order,
      amount: amount,
      payment_method_id: payment_method.id,
      gateway_transaction_id: payment_result.transaction_id,
      status: 'completed',
      processed_at: Time.current
    )
  end

  def update_order_status
    order.update!(
      status: 'paid',
      paid_at: Time.current
    )
  end

  def generate_idempotency_key
    "order_#{order.id}_#{Time.current.to_i}"
  end

  def success_result(payment_result)
    OpenStruct.new(
      success?: true,
      payment_id: payment_result.transaction_id,
      message: 'Payment processed successfully'
    )
  end

  def failure_result(error_message)
    OpenStruct.new(
      success?: false,
      error: error_message,
      message: 'Payment processing failed'
    )
  end
end