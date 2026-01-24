# frozen_string_literal: true

class DeliveryCalculationService
  STANDARD_DELIVERY_DAYS = 3
  EXPRESS_DELIVERY_DAYS = 1
  OVERNIGHT_DELIVERY_DAYS = 0

  def initialize(order)
    @order = order
    @shipping_method = order.shipping_method
    @order_date = order.created_at
  end

  def calculate_delivery_date
    delivery_days = determine_delivery_days
    
    if overnight_delivery?
      next_business_day
    else
      delivery_days.days.from_now(@order_date)
    end
  end

  def calculate_delivery_window
    start_date = calculate_delivery_date
    end_date = start_date + 1.day
    
    {
      earliest: start_date,
      latest: end_date,
      delivery_type: delivery_type_description
    }
  end

  def estimated_delivery_time
    delivery_date = calculate_delivery_date
    
    case @shipping_method
    when 'express'
      delivery_date.beginning_of_day + 12.hours
    when 'standard'
      delivery_date.beginning_of_day + 17.hours
    else
      delivery_date.beginning_of_day + 15.hours
    end
  end

  def can_deliver_on_date?(target_date)
    return false if weekend?(target_date)
    return false if holiday?(target_date)
    
    target_date >= calculate_delivery_date
  end

  private

  def determine_delivery_days
    case @shipping_method
    when 'express'
      EXPRESS_DELIVERY_DAYS
    when 'overnight'
      OVERNIGHT_DELIVERY_DAYS
    else
      STANDARD_DELIVERY_DAYS
    end
  end

  def overnight_delivery?
    @shipping_method == 'overnight'
  end

  def next_business_day
    date = @order_date + 1.day
    
    while weekend?(date) || holiday?(date)
      date += 1.day
    end
    
    date
  end

  def weekend?(date)
    date.saturday? || date.sunday?
  end

  def holiday?(date)
    HolidayService.new.holiday?(date)
  end

  def delivery_type_description
    case @shipping_method
    when 'express'
      'Express Delivery'
    when 'overnight'
      'Overnight Delivery'
    else
      'Standard Delivery'
    end
  end
end