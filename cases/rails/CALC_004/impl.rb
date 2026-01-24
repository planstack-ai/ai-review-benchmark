# frozen_string_literal: true

class PriceCalculationService
  TAX_RATE = 0.08
  DISCOUNT_THRESHOLD = 100.0
  BULK_DISCOUNT_RATE = 0.05

  def initialize(base_price, quantity = 1, discount_code = nil)
    @base_price = base_price.to_f
    @quantity = quantity.to_i
    @discount_code = discount_code
  end

  def calculate_total
    subtotal = calculate_subtotal
    discounted_amount = apply_discounts(subtotal)
    final_amount = apply_tax(discounted_amount)
    round_to_currency(final_amount)
  end

  def calculate_breakdown
    subtotal = calculate_subtotal
    discount_amount = calculate_discount_amount(subtotal)
    discounted_subtotal = subtotal - discount_amount
    tax_amount = calculate_tax_amount(discounted_subtotal)
    total = discounted_subtotal + tax_amount

    {
      subtotal: round_to_currency(subtotal),
      discount: round_to_currency(discount_amount),
      tax: round_to_currency(tax_amount),
      total: round_to_currency(total)
    }
  end

  private

  def calculate_subtotal
    @base_price * @quantity
  end

  def apply_discounts(amount)
    discount_amount = calculate_discount_amount(amount)
    amount - discount_amount
  end

  def calculate_discount_amount(amount)
    total_discount = 0.0
    
    if eligible_for_bulk_discount?(amount)
      total_discount += amount * BULK_DISCOUNT_RATE
    end
    
    if valid_discount_code?
      code_discount = calculate_code_discount(amount)
      total_discount += code_discount
    end
    
    total_discount
  end

  def eligible_for_bulk_discount?(amount)
    amount >= DISCOUNT_THRESHOLD
  end

  def valid_discount_code?
    return false unless @discount_code
    
    valid_codes = %w[SAVE10 WELCOME5 STUDENT15]
    valid_codes.include?(@discount_code.upcase)
  end

  def calculate_code_discount(amount)
    case @discount_code.upcase
    when 'SAVE10'
      amount * 0.1
    when 'WELCOME5'
      amount * 0.05
    when 'STUDENT15'
      amount * 0.15
    else
      0.0
    end
  end

  def apply_tax(amount)
    tax_amount = calculate_tax_amount(amount)
    amount + tax_amount
  end

  def calculate_tax_amount(amount)
    amount * TAX_RATE
  end

  def round_to_currency(amount)
    (amount * 100).round / 100.0
  end
end