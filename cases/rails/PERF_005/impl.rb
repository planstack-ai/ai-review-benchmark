# frozen_string_literal: true

class OrderAnalyticsService
  def initialize(date_range = nil)
    @date_range = date_range || default_date_range
  end

  def generate_sales_report
    {
      total_revenue: calculate_total_revenue,
      order_count: count_orders,
      average_order_value: calculate_average_order_value,
      top_products: find_top_products,
      status_breakdown: analyze_order_status_distribution
    }
  end

  def find_pending_orders_for_notification
    orders = Order.where(created_at: @date_range)
                  .where(notification_sent: false)
                  .where(priority_level: 'high')
                  .includes(:customer, :order_items)

    orders.select { |order| order.requires_immediate_attention? }
  end

  def calculate_fulfillment_metrics
    completed_orders = fetch_completed_orders
    pending_orders = fetch_pending_orders

    {
      completion_rate: calculate_completion_rate(completed_orders, pending_orders),
      average_processing_time: calculate_average_processing_time(completed_orders),
      bottleneck_analysis: identify_bottlenecks(pending_orders)
    }
  end

  private

  def calculate_total_revenue
    Order.where(created_at: @date_range)
         .where(status: ['completed', 'shipped'])
         .sum(:total_amount)
  end

  def count_orders
    Order.where(created_at: @date_range).count
  end

  def calculate_average_order_value
    total_revenue = calculate_total_revenue
    order_count = count_orders
    return 0 if order_count.zero?

    total_revenue / order_count
  end

  def find_top_products
    OrderItem.joins(:order, :product)
             .where(orders: { created_at: @date_range })
             .group('products.name')
             .sum(:quantity)
             .sort_by { |_, quantity| -quantity }
             .first(10)
             .to_h
  end

  def analyze_order_status_distribution
    Order.where(created_at: @date_range)
         .group(:status)
         .count
  end

  def fetch_completed_orders
    Order.where(created_at: @date_range)
         .where(status: 'completed')
         .includes(:order_items)
  end

  def fetch_pending_orders
    Order.where(created_at: @date_range)
         .where(status: 'pending')
         .includes(:customer)
  end

  def calculate_completion_rate(completed_orders, pending_orders)
    total_orders = completed_orders.count + pending_orders.count
    return 0 if total_orders.zero?

    (completed_orders.count.to_f / total_orders * 100).round(2)
  end

  def calculate_average_processing_time(completed_orders)
    return 0 if completed_orders.empty?

    total_time = completed_orders.sum do |order|
      (order.completed_at - order.created_at).to_i
    end

    total_time / completed_orders.count / 3600
  end

  def identify_bottlenecks(pending_orders)
    pending_orders.group_by(&:assigned_department)
                  .transform_values(&:count)
                  .sort_by { |_, count| -count }
                  .to_h
  end

  def default_date_range
    30.days.ago..Time.current
  end
end