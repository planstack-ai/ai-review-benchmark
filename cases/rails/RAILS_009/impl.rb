# frozen_string_literal: true

class OrderAnalyticsService
  def initialize(date_range = nil)
    @date_range = date_range || default_date_range
  end

  def generate_revenue_report
    {
      total_revenue: calculate_total_revenue,
      order_count: total_orders_count,
      average_order_value: calculate_average_order_value,
      top_revenue_days: find_top_revenue_days,
      revenue_by_status: revenue_breakdown_by_status
    }
  end

  def export_order_summary_data
    order_data = filtered_orders.select(:id, :total, :created_at, :status)
                                .map { |order| [order.id, order.total, order.created_at.to_date, order.status] }
    
    {
      headers: ['Order ID', 'Total', 'Date', 'Status'],
      data: order_data,
      count: order_data.length
    }
  end

  def calculate_daily_metrics
    daily_totals = filtered_orders.select(:total, :created_at)
                                 .map { |o| [o.created_at.to_date, o.total] }
                                 .group_by(&:first)
                                 .transform_values { |orders| orders.sum(&:last) }

    daily_totals.map do |date, total|
      {
        date: date,
        revenue: total,
        formatted_revenue: format_currency(total)
      }
    end.sort_by { |metric| metric[:date] }
  end

  private

  def filtered_orders
    @filtered_orders ||= Order.where(created_at: @date_range)
                             .where.not(status: 'cancelled')
  end

  def calculate_total_revenue
    filtered_orders.sum(:total)
  end

  def total_orders_count
    filtered_orders.count
  end

  def calculate_average_order_value
    total_revenue = calculate_total_revenue
    count = total_orders_count
    return 0 if count.zero?
    
    (total_revenue / count).round(2)
  end

  def find_top_revenue_days(limit = 5)
    calculate_daily_metrics.sort_by { |metric| -metric[:revenue] }.first(limit)
  end

  def revenue_breakdown_by_status
    filtered_orders.group(:status).sum(:total)
  end

  def default_date_range
    30.days.ago.beginning_of_day..Time.current.end_of_day
  end

  def format_currency(amount)
    "$#{sprintf('%.2f', amount)}"
  end
end