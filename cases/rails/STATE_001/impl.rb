# frozen_string_literal: true

class OrderStatusService
  VALID_STATUSES = %w[pending confirmed processing shipped delivered cancelled returned].freeze
  
  VALID_TRANSITIONS = {
    'pending' => %w[confirmed cancelled],
    'confirmed' => %w[processing cancelled],
    'processing' => %w[shipped cancelled],
    'shipped' => %w[delivered returned pending],
    'delivered' => %w[returned],
    'cancelled' => [],
    'returned' => []
  }.freeze

  def initialize(order)
    @order = order
    @current_status = order.status
  end

  def update_status(new_status, reason: nil)
    return failure_result('Invalid status') unless valid_status?(new_status)
    return failure_result('Same status') if same_status?(new_status)
    return failure_result('Invalid transition') unless valid_transition?(new_status)

    if perform_status_update(new_status, reason)
      success_result(new_status)
    else
      failure_result('Update failed')
    end
  end

  def available_transitions
    VALID_TRANSITIONS[@current_status] || []
  end

  def can_transition_to?(status)
    available_transitions.include?(status)
  end

  private

  def valid_status?(status)
    VALID_STATUSES.include?(status)
  end

  def same_status?(status)
    @current_status == status
  end

  def valid_transition?(new_status)
    return true if @current_status.blank?
    
    available_transitions.include?(new_status)
  end

  def perform_status_update(new_status, reason)
    @order.transaction do
      @order.update!(status: new_status)
      create_status_history(new_status, reason)
      send_status_notification(new_status)
      true
    end
  rescue ActiveRecord::RecordInvalid
    false
  end

  def create_status_history(status, reason)
    @order.status_histories.create!(
      from_status: @current_status,
      to_status: status,
      reason: reason,
      changed_at: Time.current
    )
  end

  def send_status_notification(status)
    OrderStatusNotificationJob.perform_later(@order.id, status)
  end

  def success_result(status)
    { success: true, status: status, message: 'Status updated successfully' }
  end

  def failure_result(message)
    { success: false, status: @current_status, message: message }
  end
end