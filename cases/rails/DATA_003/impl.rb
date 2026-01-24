# frozen_string_literal: true

class OrderUpdateService
  class OrderNotFoundError < StandardError; end
  class ValidationError < StandardError; end

  def initialize(order_id, user_id)
    @order_id = order_id
    @user_id = user_id
  end

  def call(attributes)
    validate_attributes!(attributes)
    
    order = find_order!
    validate_permissions!(order)
    
    update_order(order, attributes)
  end

  private

  attr_reader :order_id, :user_id

  def find_order!
    Order.find_by(id: order_id) || raise(OrderNotFoundError, "Order #{order_id} not found")
  end

  def validate_permissions!(order)
    return if order.user_id == user_id || admin_user?
    
    raise ValidationError, "Insufficient permissions to update order"
  end

  def validate_attributes!(attributes)
    required_fields = %w[status shipping_address]
    missing_fields = required_fields.select { |field| attributes[field].blank? }
    
    return if missing_fields.empty?
    
    raise ValidationError, "Missing required fields: #{missing_fields.join(', ')}"
  end

  def update_order(order, attributes)
    sanitized_attributes = sanitize_attributes(attributes)
    
    order.update!(sanitized_attributes.merge(updated_by: user_id, updated_at: Time.current))
    
    log_order_update(order, sanitized_attributes)
    send_update_notification(order) if status_changed?(sanitized_attributes)
    
    order
  end

  def sanitize_attributes(attributes)
    allowed_attributes = %w[status shipping_address notes priority customer_notes]
    attributes.slice(*allowed_attributes)
  end

  def status_changed?(attributes)
    attributes.key?('status')
  end

  def log_order_update(order, attributes)
    OrderAuditLog.create!(
      order_id: order.id,
      user_id: user_id,
      action: 'update',
      changes: attributes,
      timestamp: Time.current
    )
  end

  def send_update_notification(order)
    OrderUpdateNotificationJob.perform_later(order.id, user_id)
  end

  def admin_user?
    User.find_by(id: user_id)&.admin? || false
  end
end