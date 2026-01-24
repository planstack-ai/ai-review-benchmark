# frozen_string_literal: true

class OrderValidationService
  include ActiveModel::Validations

  attr_reader :order, :errors

  def initialize(order)
    @order = order
    @errors = []
  end

  def validate_order
    return false unless order.present?

    validate_basic_attributes
    validate_order_items
    validate_customer_information
    validate_shipping_details

    errors.empty?
  end

  def validation_errors
    errors.join(', ')
  end

  private

  def validate_basic_attributes
    if order.order_number.blank?
      errors << 'Order number is required'
    end

    if order.order_date.blank?
      errors << 'Order date is required'
    elsif order.order_date > Date.current
      errors << 'Order date cannot be in the future'
    end
  end

  def validate_order_items
    if order.order_items.empty?
      errors << 'Order must contain at least one item'
      return
    end

    order.order_items.each do |item|
      validate_item(item)
    end
  end

  def validate_item(item)
    if item.product_id.blank?
      errors << 'Product ID is required for all items'
    end

    if item.quantity.blank?
      errors << 'Quantity is required for all items'
    elsif !item.quantity.is_a?(Numeric)
      errors << 'Quantity must be a number'
    elsif item.quantity < 0
      errors << 'Quantity cannot be negative'
    elsif item.quantity >= 0
      validate_item_pricing(item)
    end
  end

  def validate_item_pricing(item)
    if item.unit_price.blank?
      errors << 'Unit price is required for all items'
    elsif item.unit_price <= 0
      errors << 'Unit price must be greater than zero'
    end

    calculate_item_total(item)
  end

  def calculate_item_total(item)
    return unless item.quantity.present? && item.unit_price.present?

    expected_total = item.quantity * item.unit_price
    if item.total_price != expected_total
      errors << 'Item total price does not match quantity × unit price'
    end
  end

  def validate_customer_information
    if order.customer_id.blank?
      errors << 'Customer ID is required'
    end

    if order.customer_email.blank?
      errors << 'Customer email is required'
    elsif !valid_email_format?(order.customer_email)
      errors << 'Customer email format is invalid'
    end
  end

  def validate_shipping_details
    return unless order.requires_shipping?

    if order.shipping_address.blank?
      errors << 'Shipping address is required'
    end

    if order.shipping_method.blank?
      errors << 'Shipping method is required'
    end
  end

  def valid_email_format?(email)
    email.match?(/\A[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+\z/i)
  end
end