# frozen_string_literal: true

class OrderProcessingService
  class ProcessingError < StandardError; end
  class PaymentError < StandardError; end

  def initialize(user, cart_items, payment_method)
    @user = user
    @cart_items = cart_items
    @payment_method = payment_method
  end

  def call
    validate_inputs
    
    ActiveRecord::Base.transaction do
      create_order
      process_line_items
      update_inventory
      charge_payment
      send_confirmation_email
    end

    @order
  rescue PaymentError => e
    Rails.logger.error "Payment failed for order #{@order&.id}: #{e.message}"
    raise ProcessingError, "Payment processing failed"
  rescue StandardError => e
    Rails.logger.error "Order processing failed: #{e.message}"
    raise ProcessingError, "Unable to process order"
  end

  private

  def validate_inputs
    raise ProcessingError, "User is required" unless @user
    raise ProcessingError, "Cart cannot be empty" if @cart_items.blank?
    raise ProcessingError, "Payment method is required" unless @payment_method
  end

  def create_order
    @order = Order.create!(
      user: @user,
      status: 'pending',
      total_amount: calculate_total_amount,
      payment_method_id: @payment_method.id,
      order_number: generate_order_number
    )
  end

  def process_line_items
    @cart_items.each do |item|
      @order.line_items.create!(
        product: item[:product],
        quantity: item[:quantity],
        unit_price: item[:product].price,
        total_price: item[:quantity] * item[:product].price
      )
    end
  end

  def update_inventory
    @cart_items.each do |item|
      product = item[:product]
      new_quantity = product.inventory_count - item[:quantity]
      
      if new_quantity < 0
        raise ProcessingError, "Insufficient inventory for #{product.name}"
      end
      
      product.update!(inventory_count: new_quantity)
    end
  end

  def charge_payment
    payment_response = PaymentGateway.charge(
      amount: @order.total_amount,
      payment_method: @payment_method,
      order_id: @order.id
    )

    unless payment_response.success?
      raise PaymentError, payment_response.error_message
    end

    @order.update!(
      status: 'paid',
      payment_transaction_id: payment_response.transaction_id
    )
  end

  def send_confirmation_email
    OrderMailer.confirmation_email(@order).deliver_later
  end

  def calculate_total_amount
    @cart_items.sum { |item| item[:quantity] * item[:product].price }
  end

  def generate_order_number
    "ORD-#{Time.current.strftime('%Y%m%d')}-#{SecureRandom.hex(4).upcase}"
  end
end