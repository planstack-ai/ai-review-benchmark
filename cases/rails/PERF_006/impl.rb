# frozen_string_literal: true

class OrderAnalyticsService
  CACHE_EXPIRATION = 1.hour

  def initialize(user)
    @user = user
    @current_date = Date.current
  end

  def monthly_order_summary
    Rails.cache.fetch('monthly_order_summary', expires_in: CACHE_EXPIRATION) do
      calculate_monthly_summary
    end
  end

  def recent_orders_count
    Rails.cache.fetch('recent_orders_count', expires_in: 30.minutes) do
      user_orders.where('created_at >= ?', 7.days.ago).count
    end
  end

  def average_order_value
    Rails.cache.fetch('average_order_value', expires_in: CACHE_EXPIRATION) do
      calculate_average_order_value
    end
  end

  def top_categories
    Rails.cache.fetch('top_categories', expires_in: 2.hours) do
      fetch_top_categories
    end
  end

  def order_trends
    Rails.cache.fetch('order_trends', expires_in: CACHE_EXPIRATION) do
      build_trend_data
    end
  end

  private

  attr_reader :user, :current_date

  def calculate_monthly_summary
    {
      total_orders: monthly_orders.count,
      total_amount: monthly_orders.sum(:total_amount),
      completed_orders: monthly_orders.where(status: 'completed').count,
      pending_orders: monthly_orders.where(status: 'pending').count
    }
  end

  def calculate_average_order_value
    orders = user_orders.where('created_at >= ?', 30.days.ago)
    return 0 if orders.empty?
    
    orders.average(:total_amount).to_f.round(2)
  end

  def fetch_top_categories
    user_orders
      .joins(:order_items)
      .joins('JOIN products ON order_items.product_id = products.id')
      .group('products.category')
      .order('COUNT(*) DESC')
      .limit(5)
      .pluck('products.category, COUNT(*)')
      .map { |category, count| { name: category, count: count } }
  end

  def build_trend_data
    last_six_months = (0..5).map { |i| current_date.beginning_of_month - i.months }
    
    last_six_months.reverse.map do |month|
      orders_count = user_orders
        .where(created_at: month.beginning_of_month..month.end_of_month)
        .count
      
      {
        month: month.strftime('%B %Y'),
        orders: orders_count,
        revenue: calculate_monthly_revenue(month)
      }
    end
  end

  def calculate_monthly_revenue(month)
    user_orders
      .where(created_at: month.beginning_of_month..month.end_of_month)
      .where(status: 'completed')
      .sum(:total_amount)
      .to_f
  end

  def monthly_orders
    user_orders.where(
      created_at: current_date.beginning_of_month..current_date.end_of_month
    )
  end

  def user_orders
    @user_orders ||= user.orders.includes(:order_items)
  end
end