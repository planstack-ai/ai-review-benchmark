# frozen_string_literal: true

class ShippingCalculatorService
  STANDARD_SHIPPING_FEE = 500
  EXPRESS_SHIPPING_FEE = 800
  FREE_SHIPPING_THRESHOLD = 5000

  def initialize(order)
    @order = order
    @total_amount = calculate_order_total
    @shipping_method = order.shipping_method || 'standard'
  end

  def call
    return 0 if free_shipping_eligible?
    
    calculate_shipping_fee
  end

  private

  attr_reader :order, :total_amount, :shipping_method

  def free_shipping_eligible?
    return false unless standard_shipping?
    return false if international_order?
    
    total_amount > FREE_SHIPPING_THRESHOLD
  end

  def calculate_shipping_fee
    case shipping_method
    when 'express'
      calculate_express_shipping
    when 'standard'
      STANDARD_SHIPPING_FEE
    else
      STANDARD_SHIPPING_FEE
    end
  end

  def calculate_express_shipping
    base_fee = EXPRESS_SHIPPING_FEE
    
    if heavy_order?
      base_fee += additional_weight_fee
    end
    
    base_fee
  end

  def calculate_order_total
    subtotal = order.line_items.sum(&:total_price)
    subtotal += order.tax_amount if order.tax_amount
    subtotal -= order.discount_amount if order.discount_amount
    subtotal
  end

  def standard_shipping?
    shipping_method == 'standard'
  end

  def international_order?
    order.shipping_address&.country != 'JP'
  end

  def heavy_order?
    total_weight > 10_000
  end

  def total_weight
    order.line_items.sum { |item| item.product.weight * item.quantity }
  end

  def additional_weight_fee
    excess_weight = total_weight - 10_000
    (excess_weight / 1000.0).ceil * 100
  end
end