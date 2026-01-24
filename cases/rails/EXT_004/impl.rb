# frozen_string_literal: true

class OrderRetryService
  include ActiveModel::Model
  include ActiveModel::Attributes

  attribute :user_id, :integer
  attribute :product_id, :integer
  attribute :quantity, :integer, default: 1
  attribute :payment_method_id, :integer
  attribute :shipping_address_id, :integer
  attribute :retry_count, :integer, default: 0

  validates :user_id, :product_id, :payment_method_id, :shipping_address_id, presence: true
  validates :quantity, numericality: { greater_than: 0 }
  validates :retry_count, numericality: { greater_than_or_equal_to: 0 }

  MAX_RETRY_ATTEMPTS = 3
  RETRY_DELAY = 2.seconds

  def call
    return failure_result('Invalid parameters') unless valid?
    return failure_result('Maximum retry attempts exceeded') if retry_count > MAX_RETRY_ATTEMPTS

    begin
      process_order_with_retry
    rescue StandardError => e
      Rails.logger.error "Order retry failed: #{e.message}"
      handle_retry_failure(e)
    end
  end

  private

  def process_order_with_retry
    order = create_order
    
    if order.persisted?
      process_payment(order)
      success_result(order)
    else
      increment_retry_and_reprocess
    end
  end

  def create_order
    Order.create(
      user_id: user_id,
      product_id: product_id,
      quantity: quantity,
      payment_method_id: payment_method_id,
      shipping_address_id: shipping_address_id,
      status: 'pending',
      total_amount: calculate_total_amount,
      created_at: Time.current
    )
  end

  def process_payment(order)
    payment_service = PaymentProcessingService.new(
      order: order,
      payment_method_id: payment_method_id
    )
    
    payment_result = payment_service.process
    
    if payment_result.success?
      order.update!(status: 'confirmed', payment_status: 'completed')
    else
      order.update!(status: 'failed', payment_status: 'failed')
      raise PaymentProcessingError, payment_result.error_message
    end
  end

  def calculate_total_amount
    product = Product.find(product_id)
    base_amount = product.price * quantity
    shipping_cost = calculate_shipping_cost
    base_amount + shipping_cost
  end

  def calculate_shipping_cost
    ShippingCalculator.new(
      product_id: product_id,
      quantity: quantity,
      shipping_address_id: shipping_address_id
    ).calculate
  end

  def increment_retry_and_reprocess
    if retry_count < MAX_RETRY_ATTEMPTS
      sleep(RETRY_DELAY)
      self.retry_count += 1
      process_order_with_retry
    else
      failure_result('Order creation failed after maximum retries')
    end
  end

  def handle_retry_failure(error)
    if retry_count < MAX_RETRY_ATTEMPTS && retryable_error?(error)
      increment_retry_and_reprocess
    else
      failure_result("Order processing failed: #{error.message}")
    end
  end

  def retryable_error?(error)
    error.is_a?(ActiveRecord::ConnectionTimeoutError) ||
      error.is_a?(Net::TimeoutError) ||
      error.is_a?(PaymentProcessingError)
  end

  def success_result(order)
    OpenStruct.new(success?: true, order: order, error_message: nil)
  end

  def failure_result(message)
    OpenStruct.new(success?: false, order: nil, error_message: message)
  end
end