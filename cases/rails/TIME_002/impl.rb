# frozen_string_literal: true

class SalePeriodService
  attr_reader :sale, :start_date, :end_date

  def initialize(sale)
    @sale = sale
    @start_date = sale.start_date
    @end_date = sale.end_date
  end

  def self.active_sales
    current_time = Time.current
    Sale.joins(:sale_periods)
        .where('sale_periods.start_date <= ? AND sale_periods.end_date >= ?', 
               current_time, current_time)
        .distinct
  end

  def self.upcoming_sales(days_ahead = 7)
    future_date = days_ahead.days.from_now
    Sale.joins(:sale_periods)
        .where('sale_periods.start_date BETWEEN ? AND ?', 
               Time.current, future_date)
        .distinct
  end

  def active?
    current_time = Time.current
    current_time >= sale_start_time && current_time <= sale_end_time
  end

  def starts_today?
    Date.current == start_date.to_date
  end

  def ends_today?
    Date.current == end_date.to_date
  end

  def time_until_start
    return 0 if active? || expired?
    sale_start_time - Time.current
  end

  def time_until_end
    return 0 if expired?
    return sale_end_time - Time.current if active?
    duration
  end

  def duration
    sale_end_time - sale_start_time
  end

  def expired?
    Time.current > sale_end_time
  end

  def overlaps_with?(other_service)
    return false unless other_service.is_a?(self.class)
    
    sale_start_time < other_service.sale_end_time && 
    sale_end_time > other_service.sale_start_time
  end

  def status
    return :expired if expired?
    return :active if active?
    :upcoming
  end

  def formatted_period
    "#{sale_start_time.strftime('%B %d, %Y at %I:%M %p')} - #{sale_end_time.strftime('%B %d, %Y at %I:%M %p')}"
  end

  private

  def sale_start_time
    @sale_start_time ||= start_date
  end

  def sale_end_time
    @sale_end_time ||= end_date.end_of_day
  end
end