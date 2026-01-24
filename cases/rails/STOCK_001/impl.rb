# frozen_string_literal: true

class StockAllocationService
  class InsufficientStockError < StandardError; end
  class AllocationError < StandardError; end

  def initialize(user)
    @user = user
    @cart = user.cart
  end

  def add_item_to_cart(product, quantity)
    return false unless product&.available?

    ActiveRecord::Base.transaction do
      cart_item = find_or_initialize_cart_item(product)
      new_quantity = cart_item.quantity + quantity

      validate_stock_availability(product, new_quantity)
      reserve_stock_for_item(product, quantity)
      
      cart_item.quantity = new_quantity
      cart_item.save!
      
      update_cart_totals
      true
    end
  rescue InsufficientStockError, AllocationError
    false
  end

  def remove_item_from_cart(product, quantity = nil)
    cart_item = @cart.cart_items.find_by(product: product)
    return false unless cart_item

    ActiveRecord::Base.transaction do
      quantity_to_remove = quantity || cart_item.quantity
      release_reserved_stock(product, quantity_to_remove)
      
      if quantity && cart_item.quantity > quantity
        cart_item.quantity -= quantity
        cart_item.save!
      else
        cart_item.destroy!
      end
      
      update_cart_totals
      true
    end
  end

  def process_checkout
    return false if @cart.cart_items.empty?

    ActiveRecord::Base.transaction do
      validate_all_reservations
      create_order_from_cart
      clear_cart_and_reservations
      true
    end
  rescue StandardError
    false
  end

  private

  def find_or_initialize_cart_item(product)
    @cart.cart_items.find_or_initialize_by(product: product) do |item|
      item.quantity = 0
      item.unit_price = product.price
    end
  end

  def validate_stock_availability(product, requested_quantity)
    available_stock = product.stock_quantity - product.reserved_quantity
    raise InsufficientStockError if available_stock < requested_quantity
  end

  def reserve_stock_for_item(product, quantity)
    result = product.increment(:reserved_quantity, quantity)
    raise AllocationError unless result
    
    StockReservation.create!(
      user: @user,
      product: product,
      quantity: quantity,
      expires_at: 30.minutes.from_now
    )
  end

  def release_reserved_stock(product, quantity)
    product.decrement(:reserved_quantity, quantity)
    
    reservation = StockReservation.find_by(
      user: @user,
      product: product
    )
    
    if reservation
      if reservation.quantity <= quantity
        reservation.destroy!
      else
        reservation.update!(quantity: reservation.quantity - quantity)
      end
    end
  end

  def validate_all_reservations
    @cart.cart_items.each do |item|
      validate_stock_availability(item.product, item.quantity)
    end
  end

  def create_order_from_cart
    order = Order.create!(
      user: @user,
      total_amount: @cart.total_amount,
      status: 'pending'
    )

    @cart.cart_items.each do |cart_item|
      order.order_items.create!(
        product: cart_item.product,
        quantity: cart_item.quantity,
        unit_price: cart_item.unit_price
      )
    end

    order
  end

  def clear_cart_and_reservations
    StockReservation.where(user: @user).destroy_all
    @cart.cart_items.destroy_all
    @cart.update!(total_amount: 0)
  end

  def update_cart_totals
    @cart.update!(
      total_amount: @cart.cart_items.sum { |item| item.quantity * item.unit_price }
    )
  end
end