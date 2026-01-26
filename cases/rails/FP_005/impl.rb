# frozen_string_literal: true

class OrderProcessingService
  include ActiveModel::Model
  include ActiveModel::Callbacks

  define_model_callbacks :process, :validate_order, :payment

  attr_accessor :order, :user, :payment_method, :shipping_address

  def initialize(order:, user:, payment_method: nil, shipping_address: nil)
    @order = order
    @user = user
    @payment_method = payment_method
    @shipping_address = shipping_address
  end

  def call
    ActiveRecord::Base.transaction do
      run_callbacks :process do
        return failure_result('Invalid order data') unless valid_order_data?

        run_callbacks :validate_order do
          validate_inventory
          calculate_totals
        end

        run_callbacks :payment do
          process_payment if payment_method.present?
          update_order_status
        end

        send_confirmation_email
        success_result
      end
    end
  rescue StandardError => e
    failure_result(e.message)
  end

  private

  def valid_order_data?
    order.present? && user.present? && order.order_items.any?
  end

  def validate_inventory
    order.order_items.each do |item|
      product = item.product
      raise "Insufficient inventory for #{product.name}" if product.stock_quantity < item.quantity
    end
  end

  def calculate_totals
    subtotal = order.order_items.sum { |item| item.quantity * item.unit_price }
    tax_amount = subtotal * tax_rate
    shipping_cost = calculate_shipping_cost(subtotal)

    order.update!(
      subtotal: subtotal,
      tax_amount: tax_amount,
      shipping_cost: shipping_cost,
      total_amount: subtotal + tax_amount + shipping_cost
    )
  end

  def process_payment
    payment_result = PaymentGateway.charge(
      amount: order.total_amount,
      payment_method: payment_method,
      customer: user
    )

    raise 'Payment processing failed' unless payment_result.success?

    order.update!(payment_status: 'paid', payment_reference: payment_result.transaction_id)
  end

  def update_order_status
    order.update!(status: 'confirmed', confirmed_at: Time.current)
    update_inventory
  end

  def update_inventory
    order.order_items.each do |item|
      item.product.decrement!(:stock_quantity, item.quantity)
    end
  end

  def send_confirmation_email
    OrderMailer.confirmation_email(order).deliver_later
  end

  def calculate_shipping_cost(amount)
    return 0 if amount > 100
    shipping_address&.international? ? 25.00 : 10.00
  end

  def tax_rate
    shipping_address&.tax_rate || 0.08
  end

  def success_result
    { success: true, order: order }
  end

  def failure_result(message)
    { success: false, error: message }
  end
end