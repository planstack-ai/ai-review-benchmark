# frozen_string_literal: true

class ShippingService
  include ActiveModel::Model

  attr_accessor :order, :shipping_address, :shipping_method

  def initialize(order:, shipping_address:, shipping_method: 'standard')
    @order = order
    @shipping_address = shipping_address
    @shipping_method = shipping_method
    @api_client = ShippingApiClient.new
  end

  def create_shipment
    return false unless valid_order?

    shipment_data = build_shipment_payload
    response = submit_shipment_request(shipment_data)
    
    if response
      update_order_with_tracking(response)
      send_confirmation_email
      true
    else
      false
    end
  end

  def calculate_shipping_cost
    return 0 unless valid_order?

    cost_data = build_cost_payload
    response = submit_cost_request(cost_data)
    
    response&.dig('cost', 'total') || 0
  end

  def track_shipment(tracking_number)
    response = submit_tracking_request(tracking_number)
    parse_tracking_response(response) if response
  end

  private

  def valid_order?
    order.present? && 
    order.items.any? && 
    shipping_address.present? &&
    shipping_address.valid?
  end

  def build_shipment_payload
    {
      order_id: order.id,
      items: order.items.map { |item| format_item(item) },
      destination: format_address(shipping_address),
      service_type: shipping_method,
      insurance_value: order.total_value
    }
  end

  def build_cost_payload
    {
      items: order.items.map { |item| format_item_for_cost(item) },
      destination: format_address(shipping_address),
      service_type: shipping_method
    }
  end

  def submit_shipment_request(payload)
    @api_client.create_shipment(payload) rescue nil
  end

  def submit_cost_request(payload)
    @api_client.calculate_cost(payload) rescue nil
  end

  def submit_tracking_request(tracking_number)
    @api_client.track_package(tracking_number) rescue nil
  end

  def format_item(item)
    {
      sku: item.sku,
      quantity: item.quantity,
      weight: item.weight,
      dimensions: item.dimensions
    }
  end

  def format_item_for_cost(item)
    format_item(item).merge(value: item.unit_price)
  end

  def format_address(address)
    {
      name: address.full_name,
      street: address.street_address,
      city: address.city,
      state: address.state,
      zip: address.postal_code,
      country: address.country_code
    }
  end

  def update_order_with_tracking(response)
    order.update!(
      tracking_number: response['tracking_number'],
      shipping_status: 'shipped',
      shipped_at: Time.current
    )
  end

  def send_confirmation_email
    OrderMailer.shipping_confirmation(order).deliver_later
  end

  def parse_tracking_response(response)
    return unless response['status']
    
    {
      status: response['status'],
      location: response['current_location'],
      estimated_delivery: response['estimated_delivery_date'],
      events: response['tracking_events'] || []
    }
  end
end