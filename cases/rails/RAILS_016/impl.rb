# frozen_string_literal: true

class OrderProcessingService
  include ActiveModel::Model

  attr_accessor :order, :user, :payment_method

  before_validation :normalize_order_data
  before_validation :validate_inventory
  after_validation :calculate_totals
  before_save :process_payment
  before_save :reserve_inventory
  after_save :send_confirmation_email
  after_save :update_analytics
  after_save :trigger_fulfillment

  def initialize(order:, user:, payment_method:)
    @order = order
    @user = user
    @payment_method = payment_method
    @callbacks_executed = []
  end

  def process
    return false unless valid?
    
    execute_before_save_callbacks
    save_order
    execute_after_save_callbacks
    
    true
  rescue StandardError => e
    rollback_changes
    Rails.logger.error "Order processing failed: #{e.message}"
    false
  end

  private

  def normalize_order_data
    @order.email = @order.email&.downcase&.strip
    @order.phone = normalize_phone_number(@order.phone)
    @callbacks_executed << :normalize_order_data
  end

  def validate_inventory
    @order.line_items.each do |item|
      available_quantity = InventoryService.available_quantity(item.product_id)
      if item.quantity > available_quantity
        errors.add(:base, "Insufficient inventory for #{item.product.name}")
      end
    end
    @callbacks_executed << :validate_inventory
  end

  def calculate_totals
    @order.subtotal = @order.line_items.sum(&:total_price)
    @order.tax_amount = TaxCalculator.calculate(@order.subtotal, @order.shipping_address)
    @order.shipping_cost = ShippingCalculator.calculate(@order)
    @order.total = @order.subtotal + @order.tax_amount + @order.shipping_cost
    @callbacks_executed << :calculate_totals
  end

  def process_payment
    payment_result = PaymentProcessor.charge(
      amount: @order.total,
      payment_method: @payment_method,
      customer: @user
    )
    
    if payment_result.success?
      @order.payment_status = 'paid'
      @order.transaction_id = payment_result.transaction_id
    else
      errors.add(:payment, payment_result.error_message)
      return false
    end
    
    @callbacks_executed << :process_payment
  end

  def reserve_inventory
    @order.line_items.each do |item|
      InventoryService.reserve(item.product_id, item.quantity)
    end
    @callbacks_executed << :reserve_inventory
  end

  def save_order
    @order.status = 'confirmed'
    @order.save!
  end

  def send_confirmation_email
    OrderMailer.confirmation_email(@order, @user).deliver_later
    @callbacks_executed << :send_confirmation_email
  end

  def update_analytics
    AnalyticsService.track_order_completion(@order, @user)
    @callbacks_executed << :update_analytics
  end

  def trigger_fulfillment
    FulfillmentService.create_shipment(@order)
    @callbacks_executed << :trigger_fulfillment
  end

  def execute_before_save_callbacks
    process_payment
    reserve_inventory
  end

  def execute_after_save_callbacks
    send_confirmation_email
    update_analytics
    trigger_fulfillment
  end

  def rollback_changes
    if @callbacks_executed.include?(:reserve_inventory)
      @order.line_items.each do |item|
        InventoryService.release_reservation(item.product_id, item.quantity)
      end
    end
    
    if @callbacks_executed.include?(:process_payment) && @order.transaction_id
      PaymentProcessor.refund(@order.transaction_id)
    end
  end

  def normalize_phone_number(phone)
    return nil unless phone
    phone.gsub(/\D/, '').gsub(/^1/, '')
  end
end