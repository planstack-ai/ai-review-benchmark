# frozen_string_literal: true

class OrderTaxCalculationService
  TAX_RATE = 0.10
  
  def initialize(order)
    @order = order
    @subtotal = calculate_subtotal
    @discount_amount = calculate_discount_amount
  end

  def call
    {
      subtotal: @subtotal,
      discount: @discount_amount,
      tax: calculate_tax,
      total: calculate_total
    }
  end

  private

  def calculate_subtotal
    @order.line_items.sum do |item|
      item.quantity * item.unit_price
    end
  end

  def calculate_discount_amount
    return 0 unless @order.discount_code.present?
    
    case @order.discount_code.discount_type
    when 'percentage'
      @subtotal * (@order.discount_code.value / 100.0)
    when 'fixed'
      [@order.discount_code.value, @subtotal].min
    else
      0
    end
  end

  def calculate_tax
    taxable_amount * TAX_RATE
  end

  def taxable_amount
    [@subtotal, 0].max
  end

  def calculate_total
    taxed_subtotal - @discount_amount
  end

  def taxed_subtotal
    @subtotal * (1 + TAX_RATE)
  end

  def format_currency(amount)
    sprintf('%.2f', amount)
  end

  def validate_order
    raise ArgumentError, 'Order cannot be nil' if @order.nil?
    raise ArgumentError, 'Order must have line items' if @order.line_items.empty?
  end
end