# frozen_string_literal: true

class PointsCalculationService
  STANDARD_POINT_RATE = 0.01
  PREMIUM_POINT_RATE = 0.02
  MINIMUM_PURCHASE_FOR_POINTS = 10.00

  def initialize(user, order)
    @user = user
    @order = order
  end

  def calculate_points
    return 0 unless eligible_for_points?

    base_points = calculate_base_points
    bonus_points = calculate_bonus_points
    
    total_points = base_points + bonus_points
    apply_point_multipliers(total_points)
  end

  private

  attr_reader :user, :order

  def eligible_for_points?
    return false if order.total < MINIMUM_PURCHASE_FOR_POINTS
    return false if order.cancelled?
    return false if user.points_suspended?
    
    true
  end

  def calculate_base_points
    point_rate = determine_point_rate
    points = order.total * point_rate
    points.round(2)
  end

  def calculate_bonus_points
    bonus = 0
    
    if first_time_customer?
      bonus += 50
    end
    
    if order.total > 100
      bonus += 25
    end
    
    if seasonal_promotion_active?
      bonus += calculate_seasonal_bonus
    end
    
    bonus
  end

  def determine_point_rate
    return PREMIUM_POINT_RATE if user.premium_member?
    STANDARD_POINT_RATE
  end

  def apply_point_multipliers(points)
    multiplier = 1.0
    
    if user.loyalty_tier == 'gold'
      multiplier = 1.5
    elsif user.loyalty_tier == 'silver'
      multiplier = 1.2
    end
    
    if weekend_bonus_active?
      multiplier *= 1.1
    end
    
    (points * multiplier).round(2)
  end

  def first_time_customer?
    user.orders.completed.count == 1
  end

  def seasonal_promotion_active?
    current_month = Date.current.month
    [11, 12, 1].include?(current_month)
  end

  def calculate_seasonal_bonus
    (order.total * 0.005).round(2)
  end

  def weekend_bonus_active?
    Date.current.saturday? || Date.current.sunday?
  end
end