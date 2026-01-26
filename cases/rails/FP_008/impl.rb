# frozen_string_literal: true

class OrderProcessingService
  VALID_STATES = %w[pending confirmed processing shipped delivered cancelled].freeze

  VALID_TRANSITIONS = {
    'pending' => %w[confirmed cancelled],
    'confirmed' => %w[processing cancelled],
    'processing' => %w[shipped cancelled],
    'shipped' => %w[delivered],
    'delivered' => [],
    'cancelled' => []
  }.freeze

  def initialize(order)
    @order = order
    @current_state = order.status
  end

  def transition_to(new_state)
    return false unless valid_transition?(new_state)

    execute_transition(new_state)
  end

  def can_transition_to?(state)
    valid_transition?(state)
  end

  def available_transitions
    VALID_TRANSITIONS[@current_state] || []
  end

  def terminal_state?
    %w[delivered cancelled].include?(@current_state)
  end

  private

  def valid_transition?(new_state)
    return false unless VALID_STATES.include?(new_state)
    return false if @current_state == new_state

    available_transitions.include?(new_state)
  end

  def execute_transition(new_state)
    ActiveRecord::Base.transaction do
      perform_state_actions(new_state)
      update_order_state(new_state)
    end

    true
  rescue StandardError => e
    Rails.logger.error "State transition failed: #{e.message}"
    false
  end

  def perform_state_actions(new_state)
    case new_state
    when 'confirmed'
      reserve_inventory
      send_confirmation_email
    when 'processing'
      validate_payment
    when 'shipped'
      send_shipping_notification
    when 'cancelled'
      release_inventory
      process_refund if payment_completed?
    end
  end

  def update_order_state(new_state)
    @order.update!(status: new_state)
    @current_state = new_state
  end

  def reserve_inventory
    raise "Inventory reservation failed" unless InventoryService.reserve_items(@order.order_items)
  end

  def release_inventory
    InventoryService.release_items(@order.order_items)
  end

  def send_confirmation_email
    OrderMailer.confirmation(@order).deliver_later
  end

  def send_shipping_notification
    OrderMailer.shipped(@order).deliver_later
  end

  def validate_payment
    payment = @order.payments.completed.first
    raise "No completed payment found" unless payment
  end

  def payment_completed?
    @order.payments.completed.exists?
  end

  def process_refund
    payment = @order.payments.completed.first
    return unless payment

    payment.update!(status: 'refunded')
  end
end
