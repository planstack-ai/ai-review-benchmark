# frozen_string_literal: true

class DeliverySchedulingService
  include ActiveModel::Model
  include ActiveModel::Attributes
  include ActiveModel::Validations

  attribute :delivery_date, :date
  attribute :customer_id, :integer
  attribute :order_id, :integer
  attribute :delivery_address, :string
  attribute :special_instructions, :string

  validates :delivery_date, presence: true
  validates :customer_id, presence: true, numericality: { greater_than: 0 }
  validates :order_id, presence: true, numericality: { greater_than: 0 }
  validates :delivery_address, presence: true, length: { minimum: 10 }

  def initialize(attributes = {})
    super
    @errors_details = []
  end

  def schedule_delivery
    return failure_result unless valid?

    begin
      delivery_slot = find_available_delivery_slot
      return failure_result('No available delivery slots') unless delivery_slot

      delivery = create_delivery_record(delivery_slot)
      notify_customer(delivery)
      update_order_status

      success_result(delivery)
    rescue StandardError => e
      Rails.logger.error "Delivery scheduling failed: #{e.message}"
      failure_result('Failed to schedule delivery')
    end
  end

  def available_dates(days_ahead = 14)
    start_date = Date.current + 1.day
    end_date = start_date + days_ahead.days
    
    (start_date..end_date).select do |date|
      next false if weekend?(date)
      next false if holiday?(date)
      available_slots_for_date(date) > 0
    end
  end

  private

  def find_available_delivery_slot
    return nil unless delivery_date

    available_slots = DeliverySlot.where(
      date: delivery_date,
      available: true
    ).order(:start_time)

    available_slots.first
  end

  def create_delivery_record(delivery_slot)
    Delivery.create!(
      customer_id: customer_id,
      order_id: order_id,
      delivery_date: delivery_date,
      delivery_slot_id: delivery_slot.id,
      address: delivery_address,
      special_instructions: special_instructions,
      status: 'scheduled'
    )
  end

  def notify_customer(delivery)
    CustomerNotificationService.new(
      customer_id: customer_id,
      delivery: delivery
    ).send_scheduling_confirmation
  end

  def update_order_status
    Order.find(order_id).update!(status: 'scheduled_for_delivery')
  end

  def weekend?(date)
    date.saturday? || date.sunday?
  end

  def holiday?(date)
    Holiday.exists?(date: date)
  end

  def available_slots_for_date(date)
    DeliverySlot.where(date: date, available: true).count
  end

  def success_result(delivery)
    OpenStruct.new(
      success: true,
      delivery: delivery,
      message: 'Delivery scheduled successfully'
    )
  end

  def failure_result(message = nil)
    error_message = message || errors.full_messages.join(', ')
    OpenStruct.new(
      success: false,
      delivery: nil,
      message: error_message
    )
  end
end