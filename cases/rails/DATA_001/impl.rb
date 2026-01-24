# frozen_string_literal: true

class OrderProcessingService
  attr_reader :order, :errors

  def initialize(order)
    @order = order
    @errors = []
  end

  def process_order
    return false unless validate_order

    ActiveRecord::Base.transaction do
      update_inventory
      create_order_items
      calculate_totals
      send_confirmation_email
    end

    true
  rescue StandardError => e
    @errors << "Order processing failed: #{e.message}"
    false
  end

  def cancel_order
    return false unless order.can_be_cancelled?

    ActiveRecord::Base.transaction do
      restore_inventory
      update_order_status
      process_refund if order.paid?
    end

    true
  rescue StandardError => e
    @errors << "Order cancellation failed: #{e.message}"
    false
  end

  private

  def validate_order
    if order.order_items.empty?
      @errors << "Order must have at least one item"
      return false
    end

    if order.customer.nil?
      @errors << "Order must have a customer"
      return false
    end

    true
  end

  def update_inventory
    order.order_items.each do |item|
      product = item.product
      if product.stock_quantity < item.quantity
        raise "Insufficient stock for product #{product.name}"
      end
      
      product.update!(stock_quantity: product.stock_quantity - item.quantity)
    end
  end

  def create_order_items
    order.cart_items.each do |cart_item|
      OrderItem.create!(
        order: order,
        product: cart_item.product,
        quantity: cart_item.quantity,
        unit_price: cart_item.product.price
      )
    end
  end

  def calculate_totals
    subtotal = order.order_items.sum { |item| item.quantity * item.unit_price }
    tax_amount = subtotal * order.tax_rate
    total_amount = subtotal + tax_amount + order.shipping_cost

    order.update!(
      subtotal: subtotal,
      tax_amount: tax_amount,
      total_amount: total_amount
    )
  end

  def restore_inventory
    order.order_items.each do |item|
      product = item.product
      product.update!(stock_quantity: product.stock_quantity + item.quantity)
    end
  end

  def update_order_status
    order.update!(status: 'cancelled', cancelled_at: Time.current)
  end

  def process_refund
    RefundService.new(order).process_refund
  end

  def send_confirmation_email
    OrderMailer.confirmation_email(order).deliver_later
  end
end