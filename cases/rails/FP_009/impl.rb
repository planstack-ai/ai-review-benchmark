# frozen_string_literal: true

class PriceCalculationService
  TAX_RATE = 0.08
  BULK_DISCOUNT_THRESHOLD = 100
  BULK_DISCOUNT_RATE = 0.15
  PREMIUM_MULTIPLIER = 1.25
  SHIPPING_BASE_RATE = 5.99
  FREE_SHIPPING_THRESHOLD = 75.00

  def initialize(items, customer_type: :standard, shipping_address: nil)
    @items = items
    @customer_type = customer_type
    @shipping_address = shipping_address
  end

  def calculate_total
    subtotal = calculate_subtotal
    discounted_subtotal = apply_bulk_discount(subtotal)
    final_subtotal = apply_customer_type_adjustment(discounted_subtotal)
    shipping_cost = calculate_shipping(final_subtotal)
    tax_amount = calculate_tax(final_subtotal)
    
    final_subtotal + shipping_cost + tax_amount
  end

  def breakdown
    subtotal = calculate_subtotal
    discounted_subtotal = apply_bulk_discount(subtotal)
    final_subtotal = apply_customer_type_adjustment(discounted_subtotal)
    shipping_cost = calculate_shipping(final_subtotal)
    tax_amount = calculate_tax(final_subtotal)

    {
      subtotal: subtotal,
      bulk_discount: subtotal - discounted_subtotal,
      customer_adjustment: discounted_subtotal - final_subtotal,
      shipping: shipping_cost,
      tax: tax_amount,
      total: final_subtotal + shipping_cost + tax_amount
    }
  end

  private

  def calculate_subtotal
    @items.sum { |item| item[:price] * item[:quantity] }
  end

  def apply_bulk_discount(subtotal)
    return subtotal unless subtotal >= BULK_DISCOUNT_THRESHOLD
    
    subtotal * (1 - BULK_DISCOUNT_RATE)
  end

  def apply_customer_type_adjustment(subtotal)
    case @customer_type
    when :premium
      subtotal * PREMIUM_MULTIPLIER
    when :employee
      subtotal * 0.9
    else
      subtotal
    end
  end

  def calculate_shipping(subtotal)
    return 0.0 if subtotal >= FREE_SHIPPING_THRESHOLD
    return 0.0 if @customer_type == :premium
    
    base_shipping = SHIPPING_BASE_RATE
    
    if international_shipping?
      base_shipping * 2.5
    else
      base_shipping
    end
  end

  def calculate_tax(subtotal)
    tax_rate = determine_tax_rate
    subtotal * tax_rate
  end

  def international_shipping?
    return false unless @shipping_address
    
    @shipping_address[:country] != 'US'
  end

  def determine_tax_rate
    return 0.0 if international_shipping?
    return TAX_RATE * 0.5 if @customer_type == :employee
    
    TAX_RATE
  end
end