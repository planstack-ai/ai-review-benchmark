# frozen_string_literal: true

class DeliveryScheduleService
  def initialize(delivery_schedule)
    @delivery_schedule = delivery_schedule
    @current_time = Time.current
  end

  def find_matching_deliveries(target_date)
    validate_target_date(target_date)
    
    matching_deliveries = []
    
    @delivery_schedule.each do |delivery|
      if delivery_matches_date?(delivery, target_date)
        matching_deliveries << prepare_delivery_info(delivery)
      end
    end
    
    sort_deliveries_by_priority(matching_deliveries)
  end

  def count_deliveries_for_date(target_date)
    validate_target_date(target_date)
    
    count = 0
    @delivery_schedule.each do |delivery|
      count += 1 if delivery_matches_date?(delivery, target_date)
    end
    
    count
  end

  def has_deliveries_on_date?(target_date)
    validate_target_date(target_date)
    
    @delivery_schedule.any? do |delivery|
      delivery_matches_date?(delivery, target_date)
    end
  end

  def next_delivery_date_after(target_date)
    validate_target_date(target_date)
    
    future_dates = @delivery_schedule.map { |d| d[:delivery_date] }
                                   .select { |date| date > target_date }
                                   .sort
    
    future_dates.first
  end

  private

  def delivery_matches_date?(delivery, target_date)
    delivery_date = delivery[:delivery_date]
    return false unless delivery_date
    
    delivery_date == target_date
  end

  def validate_target_date(target_date)
    raise ArgumentError, "Target date cannot be nil" if target_date.nil?
    raise ArgumentError, "Target date must be a Date or Time object" unless date_like?(target_date)
  end

  def date_like?(object)
    object.is_a?(Date) || object.is_a?(Time) || object.is_a?(DateTime)
  end

  def prepare_delivery_info(delivery)
    {
      id: delivery[:id],
      delivery_date: delivery[:delivery_date],
      priority: delivery[:priority] || 'normal',
      customer_id: delivery[:customer_id],
      items_count: delivery[:items]&.count || 0
    }
  end

  def sort_deliveries_by_priority(deliveries)
    priority_order = { 'urgent' => 1, 'high' => 2, 'normal' => 3, 'low' => 4 }
    
    deliveries.sort_by do |delivery|
      [priority_order[delivery[:priority]] || 5, delivery[:delivery_date]]
    end
  end
end