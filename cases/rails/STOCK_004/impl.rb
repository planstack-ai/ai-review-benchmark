# frozen_string_literal: true

class InventoryAvailabilityService
  attr_reader :product, :warehouse_id

  def initialize(product, warehouse_id = nil)
    @product = product
    @warehouse_id = warehouse_id
  end

  def available_quantity
    return 0 unless product&.active?
    
    if warehouse_specific?
      calculate_warehouse_availability
    else
      calculate_total_availability
    end
  end

  def reserve_stock(quantity)
    return false unless can_reserve?(quantity)
    
    create_reservation(quantity)
    update_availability_cache
    true
  end

  def release_reservation(reservation_id)
    reservation = find_reservation(reservation_id)
    return false unless reservation&.active?
    
    reservation.update!(status: 'released', released_at: Time.current)
    update_availability_cache
    true
  end

  def stock_summary
    {
      total_stock: total_stock_count,
      reserved_stock: reserved_stock_count,
      available_stock: available_stock_count,
      pending_orders: pending_order_count
    }
  end

  private

  def warehouse_specific?
    warehouse_id.present?
  end

  def calculate_warehouse_availability
    warehouse_stock = product.stock_items.where(warehouse_id: warehouse_id).sum(:quantity)
    [warehouse_stock, 0].max
  end

  def calculate_total_availability
    available_stock_count
  end

  def total_stock_count
    if warehouse_specific?
      product.stock_items.where(warehouse_id: warehouse_id).sum(:quantity)
    else
      product.stock_items.sum(:quantity)
    end
  end

  def reserved_stock_count
    scope = product.stock_reservations.active
    scope = scope.joins(:stock_item).where(stock_items: { warehouse_id: warehouse_id }) if warehouse_specific?
    scope.sum(:quantity)
  end

  def available_stock_count
    total_stock_count
  end

  def pending_order_count
    product.order_items.joins(:order).where(orders: { status: 'pending' }).sum(:quantity)
  end

  def can_reserve?(quantity)
    quantity > 0 && available_quantity >= quantity
  end

  def create_reservation(quantity)
    product.stock_reservations.create!(
      quantity: quantity,
      warehouse_id: warehouse_id,
      status: 'active',
      reserved_at: Time.current,
      expires_at: 24.hours.from_now
    )
  end

  def find_reservation(reservation_id)
    product.stock_reservations.find_by(id: reservation_id)
  end

  def update_availability_cache
    Rails.cache.delete("product_availability_#{product.id}_#{warehouse_id}")
  end
end