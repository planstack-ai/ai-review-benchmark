# frozen_string_literal: true

class PricingService
  attr_reader :user, :product, :quantity

  def initialize(user:, product:, quantity: 1)
    @user = user
    @product = product
    @quantity = quantity
  end

  def calculate_total_price
    unit_price = determine_unit_price
    base_total = unit_price * quantity
    apply_quantity_discounts(base_total)
  end

  def pricing_breakdown
    unit_price = determine_unit_price
    base_total = unit_price * quantity
    discount_amount = calculate_discount_amount(base_total)
    final_total = base_total - discount_amount

    {
      unit_price: unit_price,
      quantity: quantity,
      base_total: base_total,
      discount_amount: discount_amount,
      final_total: final_total,
      pricing_tier: pricing_tier_name
    }
  end

  def eligible_for_member_pricing?
    user.present? && user.member?
  end

  private

  def determine_unit_price
    return member_price if member_pricing_applicable?
    regular_price
  end

  def member_pricing_applicable?
    product.member_pricing_enabled? && member_price.present?
  end

  def member_price
    product.member_price
  end

  def regular_price
    product.regular_price
  end

  def apply_quantity_discounts(base_total)
    discount_amount = calculate_discount_amount(base_total)
    base_total - discount_amount
  end

  def calculate_discount_amount(base_total)
    return 0 unless quantity_discount_applicable?

    case quantity
    when 5..9
      base_total * 0.05
    when 10..19
      base_total * 0.10
    when 20..Float::INFINITY
      base_total * 0.15
    else
      0
    end
  end

  def quantity_discount_applicable?
    quantity >= 5 && product.quantity_discounts_enabled?
  end

  def pricing_tier_name
    return 'member' if member_pricing_applicable?
    'regular'
  end
end