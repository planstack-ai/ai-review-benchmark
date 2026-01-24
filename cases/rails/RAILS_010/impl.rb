# frozen_string_literal: true

class OrderAnalyticsService
  def initialize(date_range = nil)
    @date_range = date_range || (30.days.ago..Time.current)
  end

  def generate_report
    {
      total_orders: total_orders_count,
      revenue_breakdown: calculate_revenue_breakdown,
      top_selling_items: find_top_selling_items,
      customer_segments: analyze_customer_segments
    }
  end

  def export_detailed_orders(format: :csv)
    orders_with_items = fetch_orders_with_items
    
    case format
    when :csv
      generate_csv_export(orders_with_items)
    when :json
      generate_json_export(orders_with_items)
    else
      raise ArgumentError, "Unsupported format: #{format}"
    end
  end

  private

  def total_orders_count
    base_orders_scope.count
  end

  def calculate_revenue_breakdown
    orders = fetch_orders_with_items
    
    breakdown = {}
    orders.each do |order|
      category = determine_order_category(order)
      breakdown[category] ||= { count: 0, revenue: 0 }
      breakdown[category][:count] += 1
      breakdown[category][:revenue] += order.total_amount
    end
    
    breakdown
  end

  def find_top_selling_items
    orders = base_orders_scope.includes(:items).where(items: { status: 'shipped' })
    
    item_sales = Hash.new(0)
    orders.each do |order|
      order.items.each do |item|
        item_sales[item.product_name] += item.quantity
      end
    end
    
    item_sales.sort_by { |_, quantity| -quantity }.first(10).to_h
  end

  def analyze_customer_segments
    orders = fetch_orders_with_items
    
    segments = {
      high_value: orders.select { |o| o.total_amount > 500 }.count,
      medium_value: orders.select { |o| o.total_amount.between?(100, 500) }.count,
      low_value: orders.select { |o| o.total_amount < 100 }.count
    }
    
    segments
  end

  def fetch_orders_with_items
    base_orders_scope.includes(:items, :customer)
  end

  def base_orders_scope
    Order.where(created_at: @date_range)
  end

  def determine_order_category(order)
    return 'bulk' if order.items.sum(&:quantity) > 10
    return 'premium' if order.total_amount > 200
    'standard'
  end

  def generate_csv_export(orders)
    CSV.generate(headers: true) do |csv|
      csv << ['Order ID', 'Customer', 'Total Amount', 'Items Count', 'Status']
      
      orders.each do |order|
        csv << [
          order.id,
          order.customer.name,
          order.total_amount,
          order.items.count,
          order.status
        ]
      end
    end
  end

  def generate_json_export(orders)
    orders.map do |order|
      {
        id: order.id,
        customer_name: order.customer.name,
        total_amount: order.total_amount,
        items_count: order.items.count,
        status: order.status,
        created_at: order.created_at
      }
    end.to_json
  end
end