# frozen_string_literal: true

class OrderValidationService
  MINIMUM_ORDER_AMOUNT = 1000

  def initialize(order)
    @order = order
    @errors = []
  end

  def valid?
    validate_minimum_amount
    validate_order_items
    validate_customer_eligibility
    
    @errors.empty?
  end

  def errors
    @errors.dup
  end

  def validation_summary
    {
      valid: valid?,
      errors: errors,
      order_total: calculate_order_total,
      discount_amount: calculate_total_discount
    }
  end

  private

  def validate_minimum_amount
    subtotal = calculate_subtotal
    
    if subtotal < MINIMUM_ORDER_AMOUNT
      @errors << "Order must be at least #{MINIMUM_ORDER_AMOUNT} yen"
    end
  end

  def validate_order_items
    if @order.order_items.empty?
      @errors << "Order must contain at least one item"
    end

    @order.order_items.each do |item|
      if item.quantity <= 0
        @errors << "Item quantity must be greater than zero"
      end
      
      if item.unit_price < 0
        @errors << "Item price cannot be negative"
      end
    end
  end

  def validate_customer_eligibility
    return unless @order.customer

    if @order.customer.blocked?
      @errors << "Customer account is blocked"
    end

    if @order.customer.payment_overdue?
      @errors << "Customer has overdue payments"
    end
  end

  def calculate_subtotal
    @order.order_items.sum { |item| item.quantity * item.unit_price }
  end

  def calculate_total_discount
    base_discount = calculate_percentage_discount
    coupon_discount = calculate_coupon_discount
    loyalty_discount = calculate_loyalty_discount
    
    [base_discount + coupon_discount + loyalty_discount, calculate_subtotal * 0.5].min
  end

  def calculate_percentage_discount
    subtotal = calculate_subtotal
    return 0 unless @order.discount_percentage

    (subtotal * @order.discount_percentage / 100.0).round
  end

  def calculate_coupon_discount
    return 0 unless @order.coupon&.active?
    
    [@order.coupon.discount_amount, calculate_subtotal].min
  end

  def calculate_loyalty_discount
    return 0 unless @order.customer&.loyalty_member?
    
    (calculate_subtotal * 0.05).round
  end

  def calculate_order_total
    calculate_subtotal - calculate_total_discount
  end
end