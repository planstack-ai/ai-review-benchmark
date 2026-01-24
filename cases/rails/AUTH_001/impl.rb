# frozen_string_literal: true

class OrderViewService
  include ActiveModel::Model
  include ActiveModel::Attributes

  attribute :user_id, :integer
  attribute :order_id, :integer
  attribute :include_items, :boolean, default: false
  attribute :include_shipping, :boolean, default: false

  validates :user_id, presence: true
  validates :order_id, presence: true

  def initialize(attributes = {})
    super
    @current_user = User.find(user_id) if user_id.present?
  end

  def call
    return failure_result('Invalid parameters') unless valid?
    return failure_result('User not found') unless current_user

    order = fetch_order
    return failure_result('Order not found') unless order

    return failure_result('Access denied') unless can_access_order?(order)

    build_order_response(order)
  rescue ActiveRecord::RecordNotFound
    failure_result('Order not found')
  rescue StandardError => e
    Rails.logger.error "OrderViewService error: #{e.message}"
    failure_result('An error occurred while retrieving the order')
  end

  private

  attr_reader :current_user

  def fetch_order
    Order.find(order_id)
  end

  def can_access_order?(order)
    return false unless order
    return false unless current_user
    
    order.user_id == current_user.id
  end

  def build_order_response(order)
    response_data = {
      id: order.id,
      status: order.status,
      total_amount: order.total_amount,
      created_at: order.created_at,
      updated_at: order.updated_at
    }

    response_data[:items] = format_order_items(order) if include_items
    response_data[:shipping_info] = format_shipping_info(order) if include_shipping

    success_result(response_data)
  end

  def format_order_items(order)
    order.order_items.includes(:product).map do |item|
      {
        id: item.id,
        product_name: item.product.name,
        quantity: item.quantity,
        unit_price: item.unit_price,
        total_price: item.total_price
      }
    end
  end

  def format_shipping_info(order)
    return nil unless order.shipping_address

    {
      address: order.shipping_address.full_address,
      tracking_number: order.tracking_number,
      estimated_delivery: order.estimated_delivery_date
    }
  end

  def success_result(data)
    OpenStruct.new(success: true, data: data, error: nil)
  end

  def failure_result(error_message)
    OpenStruct.new(success: false, data: nil, error: error_message)
  end
end