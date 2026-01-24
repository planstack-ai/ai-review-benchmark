# frozen_string_literal: true

class BulkOrderCalculationService
  include ActiveModel::Validations

  validates :order_items, presence: true
  validates :discount_percentage, numericality: { greater_than_or_equal_to: 0, less_than_or_equal_to: 100 }

  def initialize(order_items:, discount_percentage: 0, tax_rate: 0.08)
    @order_items = order_items
    @discount_percentage = discount_percentage
    @tax_rate = tax_rate
  end

  def calculate_total
    return ServiceResult.new(success: false, errors: errors.full_messages) unless valid?

    subtotal = calculate_subtotal
    discount_amount = calculate_discount(subtotal)
    discounted_subtotal = subtotal - discount_amount
    tax_amount = calculate_tax(discounted_subtotal)
    final_total = discounted_subtotal + tax_amount

    ServiceResult.new(
      success: true,
      data: {
        subtotal: format_currency(subtotal),
        discount_amount: format_currency(discount_amount),
        tax_amount: format_currency(tax_amount),
        total: format_currency(final_total),
        item_count: total_item_count
      }
    )
  end

  def bulk_discount_eligible?
    total_item_count >= 100 || calculate_subtotal >= 10000
  end

  private

  attr_reader :order_items, :discount_percentage, :tax_rate

  def calculate_subtotal
    order_items.sum do |item|
      unit_price = item[:unit_price] || item['unit_price']
      quantity = item[:quantity] || item['quantity']
      
      validate_item_data(unit_price, quantity)
      unit_price * quantity
    end
  end

  def calculate_discount(subtotal)
    return 0 if discount_percentage.zero?
    
    base_discount = (subtotal * discount_percentage / 100.0)
    bulk_discount_eligible? ? base_discount * 1.15 : base_discount
  end

  def calculate_tax(amount)
    amount * tax_rate
  end

  def total_item_count
    order_items.sum { |item| item[:quantity] || item['quantity'] }
  end

  def validate_item_data(unit_price, quantity)
    raise ArgumentError, "Invalid unit_price: #{unit_price}" unless unit_price.is_a?(Numeric) && unit_price > 0
    raise ArgumentError, "Invalid quantity: #{quantity}" unless quantity.is_a?(Integer) && quantity > 0
  end

  def format_currency(amount)
    sprintf("%.2f", amount)
  end

  class ServiceResult
    attr_reader :success, :data, :errors

    def initialize(success:, data: nil, errors: [])
      @success = success
      @data = data
      @errors = errors
    end

    def success?
      success
    end

    def failure?
      !success
    end
  end
end