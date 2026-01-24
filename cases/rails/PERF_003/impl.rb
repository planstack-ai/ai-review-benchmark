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
      order_status_distribution: calculate_status_distribution
    }
  end

  def export_order_summary(format: :csv)
    orders = fetch_orders_for_export
    
    case format
    when :csv
      generate_csv_export(orders)
    when :json
      generate_json_export(orders)
    else
      raise ArgumentError, "Unsupported format: #{format}"
    end
  end

  private

  def total_orders_count
    base_orders_query.count
  end

  def calculate_revenue_breakdown
    orders = fetch_orders_with_associations
    
    orders.group_by(&:status).transform_values do |status_orders|
      status_orders.sum { |order| order.items.sum(&:total_price) }
    end
  end

  def find_top_selling_items
    orders = fetch_orders_with_associations
    
    item_sales = Hash.new(0)
    orders.each do |order|
      order.items.each do |item|
        item_sales[item.name] += item.quantity
      end
    end
    
    item_sales.sort_by { |_, quantity| -quantity }.first(10).to_h
  end

  def calculate_status_distribution
    base_orders_query.group(:status).count
  end

  def fetch_orders_for_export
    base_orders_query.includes(:items).order(:created_at)
  end

  def fetch_orders_with_associations
    base_orders_query.includes(:items, :payments, :shipments, :user)
  end

  def base_orders_query
    Order.where(created_at: @date_range)
  end

  def generate_csv_export(orders)
    CSV.generate(headers: true) do |csv|
      csv << ['Order ID', 'Customer', 'Status', 'Total Items', 'Created At']
      
      orders.each do |order|
        csv << [
          order.id,
          order.user&.email || 'Guest',
          order.status,
          order.items.count,
          order.created_at.strftime('%Y-%m-%d %H:%M')
        ]
      end
    end
  end

  def generate_json_export(orders)
    orders.map do |order|
      {
        id: order.id,
        status: order.status,
        item_count: order.items.count,
        created_at: order.created_at.iso8601
      }
    end.to_json
  end
end