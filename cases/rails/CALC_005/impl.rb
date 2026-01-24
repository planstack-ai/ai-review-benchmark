# frozen_string_literal: true

class OrderTaxCalculationService
  attr_reader :order, :tax_exempt_items

  def initialize(order)
    @order = order
    @tax_exempt_items = %w[books medical_supplies groceries]
  end

  def call
    return build_result(0.0, 0.0) if order_tax_exempt?

    taxable_subtotal = calculate_taxable_subtotal
    tax_amount = calculate_tax_amount(taxable_subtotal)
    
    build_result(taxable_subtotal, tax_amount)
  end

  private

  def order_tax_exempt?
    order.customer&.tax_exempt? || 
    order.shipping_address&.state&.downcase == 'oregon' ||
    all_items_tax_exempt?
  end

  def all_items_tax_exempt?
    order.line_items.all? { |item| tax_exempt_category?(item.product.category) }
  end

  def tax_exempt_category?(category)
    tax_exempt_items.include?(category&.downcase)
  end

  def calculate_taxable_subtotal
    taxable_amount = 0.0
    
    order.line_items.each do |line_item|
      unless tax_exempt_category?(line_item.product.category)
        item_total = line_item.quantity * line_item.unit_price
        item_total -= apply_item_discounts(line_item, item_total)
        taxable_amount += item_total
      end
    end

    taxable_amount -= order.discount_amount if order.discount_amount > 0
    [taxable_amount, 0.0].max
  end

  def apply_item_discounts(line_item, item_total)
    discount = 0.0
    
    if line_item.product.on_sale?
      discount += item_total * (line_item.product.sale_percentage / 100.0)
    end
    
    if bulk_discount_eligible?(line_item)
      discount += item_total * 0.05
    end
    
    discount
  end

  def bulk_discount_eligible?(line_item)
    line_item.quantity >= 10 && line_item.product.bulk_discount_eligible?
  end

  def calculate_tax_amount(subtotal)
    return 0.0 if subtotal <= 0

    base_tax = subtotal * 0.08
    
    if luxury_tax_applicable?
      base_tax += calculate_luxury_tax(subtotal)
    end
    
    base_tax.round(2)
  end

  def luxury_tax_applicable?
    order.line_items.any? { |item| luxury_item?(item.product) }
  end

  def luxury_item?(product)
    luxury_categories = %w[jewelry watches luxury_electronics]
    luxury_categories.include?(product.category&.downcase) || product.price > 1000
  end

  def calculate_luxury_tax(subtotal)
    luxury_items_total = order.line_items
      .select { |item| luxury_item?(item.product) }
      .sum { |item| item.quantity * item.unit_price }
    
    luxury_items_total * 0.02
  end

  def build_result(taxable_subtotal, tax_amount)
    {
      taxable_subtotal: taxable_subtotal,
      tax_amount: tax_amount,
      total_with_tax: taxable_subtotal + tax_amount,
      tax_rate_applied: tax_amount > 0 ? (tax_amount / taxable_subtotal * 100).round(2) : 0.0
    }
  end
end