# frozen_string_literal: true

class MembershipDiscountService
  MEMBER_DISCOUNT_RATE = 0.10
  TAX_RATE = 0.08

  def initialize(user, cart_items)
    @user = user
    @cart_items = cart_items
    @subtotal = calculate_subtotal
  end

  def call
    return build_result(subtotal: @subtotal, discount: 0, final_total: final_total_with_tax) unless eligible_for_discount?

    discounted_total = apply_member_discount
    final_amount = calculate_final_total(discounted_total)
    discount_amount = @subtotal - discounted_total

    build_result(
      subtotal: @subtotal,
      discount: discount_amount,
      final_total: final_amount
    )
  end

  private

  def eligible_for_discount?
    @user&.member? && @cart_items.any? && @subtotal > 0
  end

  def calculate_subtotal
    @cart_items.sum { |item| item.price * item.quantity }
  end

  def apply_member_discount
    @subtotal * MEMBER_DISCOUNT_RATE
  end

  def calculate_final_total(amount)
    amount + (amount * TAX_RATE)
  end

  def final_total_with_tax
    @subtotal + (@subtotal * TAX_RATE)
  end

  def build_result(subtotal:, discount:, final_total:)
    {
      subtotal: format_currency(subtotal),
      discount_applied: format_currency(discount),
      tax_amount: format_currency(final_total - (subtotal - discount)),
      final_total: format_currency(final_total),
      member_discount_applied: discount > 0
    }
  end

  def format_currency(amount)
    sprintf('%.2f', amount.round(2))
  end
end