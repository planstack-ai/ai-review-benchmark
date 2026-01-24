# frozen_string_literal: true

class OrderProcessingService
  attr_reader :user, :order_params, :errors

  def initialize(user, order_params)
    @user = user
    @order_params = order_params
    @errors = []
  end

  def call
    return failure_result unless valid_user?
    return failure_result unless validate_order_data

    order = create_order
    return failure_result unless order.persisted?

    process_payment(order)
    send_confirmation_email(order) if order.paid?
    update_inventory(order)

    success_result(order)
  rescue StandardError => e
    Rails.logger.error "Order processing failed: #{e.message}"
    failure_result
  end

  private

  def valid_user?
    return true if user&.active?

    @errors << "Invalid or inactive user"
    false
  end

  def validate_order_data
    required_fields = [:quantity, :product_id, :address]
    missing_fields = required_fields.reject { |field| order_params[field].present? }

    if missing_fields.any?
      @errors << "Missing required fields: #{missing_fields.join(', ')}"
      return false
    end

    validate_quantity && validate_product_exists
  end

  def validate_quantity
    quantity = order_params[:quantity].to_i
    return true if quantity > 0 && quantity <= 100

    @errors << "Quantity must be between 1 and 100"
    false
  end

  def validate_product_exists
    product = Product.find_by(id: order_params[:product_id])
    return true if product&.available?

    @errors << "Product not found or unavailable"
    false
  end

  def create_order
    Order.create(
      user: user,
      product_id: sanitized_params[:product_id],
      quantity: sanitized_params[:quantity],
      address: sanitized_params[:address],
      total_amount: calculate_total_amount,
      status: 'pending'
    )
  end

  def sanitized_params
    params[:order]
  end

  def calculate_total_amount
    product = Product.find(order_params[:product_id])
    product.price * order_params[:quantity].to_i
  end

  def process_payment(order)
    payment_service = PaymentService.new(order)
    payment_service.process
  end

  def send_confirmation_email(order)
    OrderMailer.confirmation_email(order).deliver_later
  end

  def update_inventory(order)
    InventoryService.new(order.product, order.quantity).decrement
  end

  def success_result(order)
    { success: true, order: order, errors: [] }
  end

  def failure_result
    { success: false, order: nil, errors: errors }
  end
end