# frozen_string_literal: true

class InventorySyncService
  SYNC_DELAY_THRESHOLD = 5.minutes
  MAX_RETRY_ATTEMPTS = 3

  def initialize(warehouse_id:, product_ids: [])
    @warehouse_id = warehouse_id
    @product_ids = product_ids
    @warehouse = Warehouse.find(warehouse_id)
    @sync_errors = []
  end

  def sync_inventory
    return false unless warehouse_operational?

    products_to_sync.each do |product|
      sync_product_inventory(product)
    end

    handle_sync_completion
  end

  def calculate_available_stock(product_id)
    product = Product.find(product_id)
    local_stock = fetch_local_stock(product)
    
    return 0 if local_stock <= 0
    
    available = local_stock
    
    apply_safety_buffer(available, product)
  end

  def sync_status
    {
      warehouse_id: @warehouse_id,
      last_sync: @warehouse.last_synced_at,
      pending_items: pending_sync_count,
      sync_delay: calculate_sync_delay,
      status: determine_sync_status
    }
  end

  private

  def warehouse_operational?
    @warehouse.active? && @warehouse.api_accessible?
  end

  def products_to_sync
    if @product_ids.any?
      Product.where(id: @product_ids, warehouse_id: @warehouse_id)
    else
      @warehouse.products.where('updated_at > ?', 1.hour.ago)
    end
  end

  def sync_product_inventory(product)
    external_stock = fetch_external_stock(product)
    local_stock = fetch_local_stock(product)
    
    if stock_discrepancy?(external_stock, local_stock)
      update_local_inventory(product, external_stock)
      log_inventory_adjustment(product, local_stock, external_stock)
    end
  rescue StandardError => e
    @sync_errors << { product_id: product.id, error: e.message }
  end

  def fetch_external_stock(product)
    WarehouseApiClient.new(@warehouse).get_stock_level(product.sku)
  end

  def fetch_local_stock(product)
    InventoryLevel.find_by(
      product: product,
      warehouse: @warehouse
    )&.quantity || 0
  end

  def stock_discrepancy?(external_stock, local_stock)
    (external_stock - local_stock).abs > 0
  end

  def update_local_inventory(product, new_quantity)
    inventory_level = InventoryLevel.find_or_initialize_by(
      product: product,
      warehouse: @warehouse
    )
    
    inventory_level.update!(
      quantity: new_quantity,
      last_synced_at: Time.current
    )
  end

  def apply_safety_buffer(available_stock, product)
    buffer_percentage = product.safety_buffer_percentage || 0.05
    (available_stock * (1 - buffer_percentage)).floor
  end

  def pending_sync_count
    @warehouse.inventory_levels
              .where('updated_at < ?', SYNC_DELAY_THRESHOLD.ago)
              .count
  end

  def calculate_sync_delay
    return 0 unless @warehouse.last_synced_at
    
    Time.current - @warehouse.last_synced_at
  end

  def determine_sync_status
    delay = calculate_sync_delay
    
    case delay
    when 0..SYNC_DELAY_THRESHOLD
      'current'
    when SYNC_DELAY_THRESHOLD..(SYNC_DELAY_THRESHOLD * 2)
      'delayed'
    else
      'critical'
    end
  end

  def handle_sync_completion
    @warehouse.update!(last_synced_at: Time.current)
    
    if @sync_errors.any?
      Rails.logger.warn("Inventory sync completed with #{@sync_errors.count} errors")
      false
    else
      true
    end
  end

  def log_inventory_adjustment(product, old_quantity, new_quantity)
    InventoryAdjustment.create!(
      product: product,
      warehouse: @warehouse,
      old_quantity: old_quantity,
      new_quantity: new_quantity,
      adjustment_type: 'sync',
      created_at: Time.current
    )
  end
end