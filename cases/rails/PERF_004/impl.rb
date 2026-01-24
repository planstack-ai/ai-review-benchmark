# frozen_string_literal: true

class OrderAnalyticsService
  def initialize(user)
    @user = user
  end

  def generate_summary_report
    orders = fetch_user_orders
    
    {
      total_orders: orders.count,
      total_revenue: calculate_total_revenue(orders),
      average_order_value: calculate_average_order_value(orders),
      item_statistics: calculate_item_statistics(orders),
      monthly_breakdown: generate_monthly_breakdown(orders)
    }
  end

  def calculate_fulfillment_metrics
    orders = fetch_completed_orders
    
    orders.map do |order|
      {
        order_id: order.id,
        item_count: order.items.length,
        processing_time: calculate_processing_time(order),
        fulfillment_rate: calculate_fulfillment_rate(order)
      }
    end
  end

  def export_order_data(format: :csv)
    orders = @user.orders.includes(:items, :shipping_address)
    
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

  def fetch_user_orders
    @user.orders.includes(:items, :payments)
  end

  def fetch_completed_orders
    @user.orders.where(status: 'completed').includes(:items)
  end

  def calculate_total_revenue(orders)
    orders.sum(&:total_amount)
  end

  def calculate_average_order_value(orders)
    return 0 if orders.empty?
    
    calculate_total_revenue(orders) / orders.count
  end

  def calculate_item_statistics(orders)
    total_items = orders.sum { |order| order.items.length }
    
    {
      total_items: total_items,
      average_items_per_order: orders.empty? ? 0 : total_items.to_f / orders.count,
      most_popular_items: find_most_popular_items(orders)
    }
  end

  def find_most_popular_items(orders)
    item_counts = Hash.new(0)
    
    orders.each do |order|
      order.items.each do |item|
        item_counts[item.product_name] += item.quantity
      end
    end
    
    item_counts.sort_by { |_, count| -count }.first(5).to_h
  end

  def generate_monthly_breakdown(orders)
    orders.group_by { |order| order.created_at.beginning_of_month }
          .transform_values { |monthly_orders| 
            {
              order_count: monthly_orders.count,
              revenue: monthly_orders.sum(&:total_amount),
              item_count: monthly_orders.sum { |order| order.items.length }
            }
          }
  end

  def calculate_processing_time(order)
    return nil unless order.shipped_at && order.created_at
    
    (order.shipped_at - order.created_at) / 1.day
  end

  def calculate_fulfillment_rate(order)
    return 0 if order.items.length.zero?
    
    fulfilled_items = order.items.select(&:fulfilled?).length
    (fulfilled_items.to_f / order.items.length * 100).round(2)
  end

  def generate_csv_export(orders)
    CSV.generate(headers: true) do |csv|
      csv << ['Order ID', 'Date', 'Items Count', 'Total Amount', 'Status']
      
      orders.each do |order|
        csv << [order.id, order.created_at, order.items.length, order.total_amount, order.status]
      end
    end
  end

  def generate_json_export(orders)
    orders.map do |order|
      {
        id: order.id,
        created_at: order.created_at,
        items_count: order.items.length,
        total_amount: order.total_amount,
        status: order.status
      }
    end.to_json
  end
end