# frozen_string_literal: true

class OrderReportService
  def initialize(date_range = nil)
    @date_range = date_range || default_date_range
  end

  def generate_summary_report
    orders = fetch_orders
    return empty_report if orders.empty?

    {
      total_orders: orders.count,
      total_revenue: calculate_total_revenue(orders),
      product_breakdown: generate_product_breakdown(orders),
      average_order_value: calculate_average_order_value(orders),
      top_products: identify_top_products(orders)
    }
  end

  def export_detailed_report
    orders = fetch_orders_with_details
    report_data = []

    orders.each do |order|
      order_summary = build_order_summary(order)
      report_data << order_summary
    end

    report_data
  end

  private

  def fetch_orders
    Order.where(created_at: @date_range)
         .includes(:customer)
         .order(:created_at)
  end

  def fetch_orders_with_details
    Order.where(created_at: @date_range)
         .includes(:customer, :items)
         .order(:created_at)
  end

  def build_order_summary(order)
    item_details = collect_item_details(order)
    
    {
      order_id: order.id,
      customer_name: order.customer.name,
      order_date: order.created_at.strftime('%Y-%m-%d'),
      total_amount: order.total_amount,
      items_count: order.items.count,
      item_details: item_details
    }
  end

  def collect_item_details(order)
    details = []
    
    order.items.each do |item|
      details << {
        product_name: item.product.name,
        quantity: item.quantity,
        unit_price: item.unit_price,
        total_price: item.total_price
      }
    end
    
    details
  end

  def calculate_total_revenue(orders)
    orders.sum(&:total_amount)
  end

  def calculate_average_order_value(orders)
    return 0 if orders.empty?
    calculate_total_revenue(orders) / orders.count
  end

  def generate_product_breakdown(orders)
    product_sales = Hash.new(0)
    
    orders.each do |order|
      order.items.each do |item|
        product_sales[item.product.name] += item.total_price
      end
    end
    
    product_sales
  end

  def identify_top_products(orders, limit = 5)
    product_breakdown = generate_product_breakdown(orders)
    product_breakdown.sort_by { |_, revenue| -revenue }.first(limit).to_h
  end

  def default_date_range
    30.days.ago.beginning_of_day..Time.current.end_of_day
  end

  def empty_report
    {
      total_orders: 0,
      total_revenue: 0,
      product_breakdown: {},
      average_order_value: 0,
      top_products: {}
    }
  end
end