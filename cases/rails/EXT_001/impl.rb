# frozen_string_literal: true

class PaymentProcessingService
  include ActiveModel::Validations

  PAYMENT_TIMEOUT = 30.seconds
  MAX_RETRY_ATTEMPTS = 3

  attr_reader :order, :payment_method, :amount

  def initialize(order:, payment_method:, amount:)
    @order = order
    @payment_method = payment_method
    @amount = amount
  end

  def process_payment
    validate_payment_parameters
    
    order.update!(status: 'processing_payment')
    
    begin
      payment_response = execute_payment_with_timeout
      handle_successful_payment(payment_response)
    rescue PaymentGateway::InvalidCardError => e
      handle_payment_failure('invalid_card', e.message)
    rescue PaymentGateway::InsufficientFundsError => e
      handle_payment_failure('insufficient_funds', e.message)
    rescue Timeout::Error => e
      raise PaymentTimeoutError, "Payment processing timed out after #{PAYMENT_TIMEOUT} seconds"
    rescue StandardError => e
      handle_payment_failure('processing_error', e.message)
    end
  end

  private

  def validate_payment_parameters
    raise ArgumentError, 'Order cannot be nil' if order.nil?
    raise ArgumentError, 'Payment method cannot be nil' if payment_method.nil?
    raise ArgumentError, 'Amount must be positive' if amount <= 0
  end

  def execute_payment_with_timeout
    Timeout.timeout(PAYMENT_TIMEOUT) do
      PaymentGateway.charge(
        amount: amount,
        payment_method: payment_method,
        order_id: order.id,
        idempotency_key: generate_idempotency_key
      )
    end
  end

  def handle_successful_payment(payment_response)
    order.update!(
      status: 'paid',
      payment_id: payment_response.id,
      payment_confirmed_at: Time.current
    )
    
    OrderConfirmationMailer.payment_successful(order).deliver_later
    InventoryService.new(order).reserve_items
    
    payment_response
  end

  def handle_payment_failure(error_type, error_message)
    order.update!(
      status: 'payment_failed',
      payment_error_type: error_type,
      payment_error_message: error_message,
      payment_failed_at: Time.current
    )
    
    OrderNotificationMailer.payment_failed(order).deliver_later
    
    false
  end

  def generate_idempotency_key
    "#{order.id}_#{payment_method.id}_#{Time.current.to_i}"
  end

  class PaymentTimeoutError < StandardError; end
end