# frozen_string_literal: true

class BundleStockCalculationService
  attr_reader :bundle, :errors

  def initialize(bundle)
    @bundle = bundle
    @errors = []
  end

  def call
    return failure('Bundle not found') unless bundle&.persisted?
    return failure('Bundle has no components') if bundle_components.empty?

    calculate_bundle_stock
  end

  private

  def calculate_bundle_stock
    available_stock = compute_available_stock
    
    if available_stock >= 0
      update_bundle_stock(available_stock)
      success(available_stock)
    else
      failure('Invalid stock calculation')
    end
  end

  def compute_available_stock
    active_components = filter_active_components
    return 0 if active_components.empty?

    calculate_stock_from_components(active_components)
  end

  def filter_active_components
    bundle_components.select(&:active?)
  end

  def calculate_stock_from_components(components)
    component_stocks = components.map do |component|
      adjusted_stock = component.stock - component.reserved_quantity
      [adjusted_stock, 0].max
    end

    component_stocks.sum
  end

  def update_bundle_stock(stock_amount)
    bundle.update!(
      available_stock: stock_amount,
      last_calculated_at: Time.current,
      calculation_status: 'completed'
    )
  end

  def bundle_components
    @bundle_components ||= bundle.bundle_components
                                .includes(:product)
                                .where(products: { status: 'active' })
  end

  def success(stock_amount)
    {
      success: true,
      available_stock: stock_amount,
      calculated_at: Time.current
    }
  end

  def failure(message)
    @errors << message
    {
      success: false,
      error: message,
      available_stock: 0
    }
  end
end