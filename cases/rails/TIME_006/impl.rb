# frozen_string_literal: true

class DateRangeAnalysisService
  def initialize(start_date, end_date = nil)
    @start_date = start_date.is_a?(String) ? Date.parse(start_date) : start_date
    @end_date = end_date&.is_a?(String) ? Date.parse(end_date) : end_date
  end

  def analyze_period
    return single_day_analysis if @end_date.nil?
    
    {
      total_days: calculate_total_days,
      business_days: count_business_days,
      weekend_days: count_weekend_days,
      year_transitions: detect_year_transitions,
      month_transitions: detect_month_transitions,
      quarter_boundaries: identify_quarter_boundaries
    }
  end

  def generate_daily_sequence
    return [@start_date] if @end_date.nil?
    
    sequence = []
    current_date = @start_date
    
    while current_date <= @end_date
      sequence << current_date
      current_date = next_calendar_day(current_date)
    end
    
    sequence
  end

  def find_critical_dates
    dates = generate_daily_sequence
    critical_dates = []
    
    dates.each do |date|
      critical_dates << date if year_end_date?(date)
      critical_dates << date if quarter_end_date?(date)
      critical_dates << date if month_end_date?(date)
    end
    
    critical_dates
  end

  def business_day_projection(target_business_days)
    current_date = @start_date
    business_days_counted = 0
    
    while business_days_counted < target_business_days
      if business_day?(current_date)
        business_days_counted += 1
      end
      
      break if business_days_counted >= target_business_days
      current_date = next_calendar_day(current_date)
    end
    
    current_date
  end

  private

  def single_day_analysis
    {
      date: @start_date,
      day_of_week: @start_date.strftime('%A'),
      business_day: business_day?(@start_date),
      year_end: year_end_date?(@start_date),
      month_end: month_end_date?(@start_date)
    }
  end

  def calculate_total_days
    (@end_date - @start_date).to_i + 1
  end

  def count_business_days
    generate_daily_sequence.count { |date| business_day?(date) }
  end

  def count_weekend_days
    generate_daily_sequence.count { |date| weekend_day?(date) }
  end

  def detect_year_transitions
    dates = generate_daily_sequence
    transitions = []
    
    dates.each_cons(2) do |current, next_day|
      if current.year != next_day.year
        transitions << { from: current, to: next_day }
      end
    end
    
    transitions
  end

  def detect_month_transitions
    dates = generate_daily_sequence
    dates.select { |date| date.day == 1 && date != @start_date }
  end

  def identify_quarter_boundaries
    dates = generate_daily_sequence
    dates.select { |date| [3, 6, 9, 12].include?(date.month) && date.day == Date.new(date.year, date.month, -1).day }
  end

  def next_calendar_day(date)
    Date.new(date.year, date.month, date.day + 1)
  end

  def business_day?(date)
    !weekend_day?(date)
  end

  def weekend_day?(date)
    date.saturday? || date.sunday?
  end

  def year_end_date?(date)
    date.month == 12 && date.day == 31
  end

  def month_end_date?(date)
    date == Date.new(date.year, date.month, -1)
  end

  def quarter_end_date?(date)
    [3, 6, 9, 12].include?(date.month) && month_end_date?(date)
  end
end