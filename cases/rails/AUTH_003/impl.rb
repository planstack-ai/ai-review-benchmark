# frozen_string_literal: true

class OrderReportService
  def initialize(date_range: nil, status_filter: nil)
    @date_range = date_range
    @status_filter = status_filter
  end

  def generate_report
    {
      total_orders: filtered_orders.count,
      total_revenue: calculate_total_revenue,
      orders_by_status: group_orders_by_status,
      top_customers: find_top_customers,
      average_order_value: calculate_average_order_value
    }
  end

  def export_orders_csv
    CSV.generate(headers: true) do |csv|
      csv << csv_headers
      
      filtered_orders.includes(:user, :order_items).find_each do |order|
        csv << format_order_row(order)
      end
    end
  end

  def recent_orders_summary(limit: 50)
    recent_orders = filtered_orders.order(created_at: :desc).limit(limit)
    
    {
      orders: recent_orders.map { |order| format_order_summary(order) },
      summary_stats: calculate_summary_stats(recent_orders)
    }
  end

  private

  def filtered_orders
    @filtered_orders ||= begin
      scope = orders
      scope = scope.where(created_at: @date_range) if @date_range
      scope = scope.where(status: @status_filter) if @status_filter
      scope
    end
  end

  def orders
    Order.includes(:user, :order_items)
  end

  def calculate_total_revenue
    filtered_orders.sum(:total_amount)
  end

  def group_orders_by_status
    filtered_orders.group(:status).count
  end

  def find_top_customers
    filtered_orders
      .joins(:user)
      .group('users.id', 'users.email')
      .select('users.id, users.email, COUNT(*) as order_count, SUM(orders.total_amount) as total_spent')
      .order('total_spent DESC')
      .limit(10)
  end

  def calculate_average_order_value
    total_revenue = calculate_total_revenue
    order_count = filtered_orders.count
    
    return 0 if order_count.zero?
    
    (total_revenue / order_count).round(2)
  end

  def csv_headers
    ['Order ID', 'Customer Email', 'Status', 'Total Amount', 'Created At']
  end

  def format_order_row(order)
    [
      order.id,
      order.user&.email || 'N/A',
      order.status,
      order.total_amount,
      order.created_at.strftime('%Y-%m-%d %H:%M:%S')
    ]
  end

  def format_order_summary(order)
    {
      id: order.id,
      customer_email: order.user&.email,
      status: order.status,
      total_amount: order.total_amount,
      created_at: order.created_at
    }
  end

  def calculate_summary_stats(orders_scope)
    {
      total_count: orders_scope.count,
      total_value: orders_scope.sum(:total_amount),
      status_breakdown: orders_scope.group(:status).count
    }
  end
end