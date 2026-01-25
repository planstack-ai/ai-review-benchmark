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
      log_state_change(new_state)
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
      charge_payment
      generate_picking_list
    when 'shipped'
      create_tracking_number
      send_shipping_notification
    when 'delivered'
      release_payment_hold
      trigger_review_request
    when 'cancelled'
      release_inventory
      process_refund if payment_charged?
    end
  end

  def update_order_state(new_state)
    @order.update!(
      status: new_state,
      status_changed_at: Time.current
    )
    @current_state = new_state
  end

  def log_state_change(new_state)
    @order.status_logs.create!(
      from_status: @current_state,
      to_status: new_state,
      changed_at: Time.current,
      user_id: Current.user&.id
    )
  end

  def reserve_inventory
    raise "Inventory reservation failed" unless InventoryService.reserve_items(@order.order_items)
  end

  def send_confirmation_email
    OrderMailer.confirmation(@order).deliver_later
  end

  def charge_payment
    PaymentService.charge(@order.payment_method, @order.total_amount)
  end

  def payment_charged?
    @order.payment_transactions.charged.exists?
  end
end