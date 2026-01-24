# frozen_string_literal: true

class OrderTotalCalculatorService
  include ActiveModel::Validations

  attr_reader :order, :tax_rate, :discount_amount

  validates :order, presence: true
  validates :tax_rate, presence: true, numericality: { greater_than_or_equal_to: 0 }
  validates :discount_amount, numericality: { greater_than_or_equal_to: 0 }

  def initialize(order:, tax_rate: 0.0, discount_amount: 0.0)
    @order = order
    @tax_rate = tax_rate
    @discount_amount = discount_amount
  end

  def call
    return failure_result('Invalid parameters') unless valid?
    return failure_result('Order has no items') if order.order_items.empty?

    total = calculate_total
    
    {
      success: true,
      subtotal: calculate_subtotal,
      tax_amount: calculate_tax_amount,
      discount_amount: discount_amount,
      total: total,
      currency: order.currency || 'USD'
    }
  rescue StandardError => e
    failure_result("Calculation error: #{e.message}")
  end

  private

  def calculate_total
    subtotal_with_tax = calculate_subtotal + calculate_tax_amount
    final_total = subtotal_with_tax - discount_amount
    [final_total, 0.0].max
  end

  def calculate_subtotal
    order.order_items.sum { |item| calculate_item_subtotal(item).round(2) }
  end

  def calculate_item_subtotal(item)
    base_price = item.unit_price * item.quantity
    item_discount = calculate_item_discount(item)
    base_price - item_discount
  end

  def calculate_item_discount(item)
    return 0.0 unless item.discount_percentage&.positive?
    
    discount_rate = item.discount_percentage / 100.0
    base_amount = item.unit_price * item.quantity
    base_amount * discount_rate
  end

  def calculate_tax_amount
    return 0.0 if tax_rate.zero?
    
    taxable_subtotal = calculate_subtotal
    (taxable_subtotal * tax_rate).round(2)
  end

  def failure_result(message)
    {
      success: false,
      error: message,
      subtotal: 0.0,
      tax_amount: 0.0,
      discount_amount: 0.0,
      total: 0.0
    }
  end
end