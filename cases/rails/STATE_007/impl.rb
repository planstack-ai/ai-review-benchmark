# frozen_string_literal: true

class DeliveryStatusService
  VALID_STATUSES = %i[pending processing shipped delivered cancelled].freeze
  
  FORWARD_TRANSITIONS = {
    pending: %i[processing cancelled],
    processing: %i[shipped cancelled],
    shipped: %i[delivered],
    delivered: [],
    cancelled: []
  }.freeze

  def initialize(order)
    @order = order
    @current_status = order.delivery_status&.to_sym
  end

  def update_status(new_status)
    new_status = new_status.to_sym
    
    validate_status_exists!(new_status)
    return true if current_status == new_status
    
    if valid_transition?(new_status)
      perform_status_update(new_status)
      log_status_change(new_status)
      notify_stakeholders(new_status)
      true
    else
      raise InvalidTransitionError, transition_error_message(new_status)
    end
  end

  def can_transition_to?(new_status)
    new_status = new_status.to_sym
    return false unless VALID_STATUSES.include?(new_status)
    valid_transition?(new_status)
  end

  def available_transitions
    return VALID_STATUSES if current_status.nil?
    FORWARD_TRANSITIONS[current_status] || []
  end

  private

  attr_reader :order, :current_status

  def valid_transition?(new_status)
    return true if current_status.nil?
    return true if new_status == :cancelled
    
    available_transitions.include?(new_status)
  end

  def perform_status_update(new_status)
    order.update!(delivery_status: new_status)
    update_timestamps(new_status)
  end

  def update_timestamps(new_status)
    case new_status
    when :shipped
      order.update!(shipped_at: Time.current)
    when :delivered
      order.update!(delivered_at: Time.current)
    end
  end

  def validate_status_exists!(status)
    unless VALID_STATUSES.include?(status)
      raise ArgumentError, "Invalid delivery status: #{status}"
    end
  end

  def transition_error_message(new_status)
    "Cannot transition from #{current_status} to #{new_status}"
  end

  def log_status_change(new_status)
    Rails.logger.info "Order #{order.id} status changed from #{current_status} to #{new_status}"
  end

  def notify_stakeholders(new_status)
    DeliveryNotificationJob.perform_later(order.id, new_status) if should_notify?(new_status)
  end

  def should_notify?(status)
    %i[shipped delivered cancelled].include?(status)
  end

  class InvalidTransitionError < StandardError; end
end