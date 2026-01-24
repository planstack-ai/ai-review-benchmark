# frozen_string_literal: true

class CartCheckoutService
  attr_reader :cart, :user, :errors

  def initialize(cart, user)
    @cart = cart
    @user = user
    @errors = []
  end

  def call
    return failure('Cart is empty') if cart.items.empty?
    return failure('User is invalid') unless user&.valid?

    ActiveRecord::Base.transaction do
      validate_cart_items
      calculate_totals
      create_order
      clear_cart

      return failure(errors.join(', ')) if errors.any?

      success(order)
    end
  rescue StandardError => e
    failure("Checkout failed: #{e.message}")
  end

  private

  attr_reader :order, :subtotal, :tax_amount, :total_amount

  def validate_cart_items
    cart.items.each do |item|
      product = item.product
      
      unless product.active?
        errors << "Product #{product.name} is no longer available"
        next
      end

      if item.quantity <= 0
        errors << "Invalid quantity for #{product.name}"
      end

      if product.price != item.unit_price
        item.update!(unit_price: product.price)
      end
    end
  end

  def calculate_totals
    @subtotal = cart.items.sum { |item| item.quantity * item.unit_price }
    @tax_amount = subtotal * tax_rate
    @total_amount = subtotal + tax_amount
  end

  def create_order
    @order = Order.create!(
      user: user,
      subtotal: subtotal,
      tax_amount: tax_amount,
      total_amount: total_amount,
      status: 'pending'
    )

    cart.items.each do |cart_item|
      product = cart_item.product
      
      OrderItem.create!(
        order: order,
        product: product,
        quantity: cart_item.quantity,
        unit_price: cart_item.unit_price,
        total_price: cart_item.quantity * cart_item.unit_price
      )

      product.decrement!(:stock_quantity, cart_item.quantity)
    end
  end

  def clear_cart
    cart.items.destroy_all
  end

  def tax_rate
    @tax_rate ||= user.tax_rate || 0.08
  end

  def success(data)
    OpenStruct.new(success?: true, data: data, errors: [])
  end

  def failure(message)
    OpenStruct.new(success?: false, data: nil, errors: [message])
  end
end