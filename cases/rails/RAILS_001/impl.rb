# frozen_string_literal: true

class ProductAnalyticsService
  def initialize(date_range = nil)
    @date_range = date_range || 30.days.ago..Time.current
  end

  def generate_report
    {
      total_active_products: count_active_products,
      revenue_by_category: calculate_revenue_by_category,
      top_performing_products: find_top_performers,
      inventory_status: check_inventory_levels,
      conversion_metrics: calculate_conversion_rates
    }
  end

  def export_active_products_csv
    products = Product.where(status: 'active').includes(:category, :reviews)
    
    CSV.generate(headers: true) do |csv|
      csv << ['Name', 'Category', 'Price', 'Stock', 'Rating']
      
      products.each do |product|
        csv << [
          product.name,
          product.category.name,
          product.price,
          product.stock_quantity,
          product.average_rating
        ]
      end
    end
  end

  def bulk_update_pricing(percentage_change)
    active_products = Product.where(status: 'active')
    
    active_products.find_each do |product|
      new_price = calculate_new_price(product.price, percentage_change)
      product.update!(price: new_price)
    end
    
    active_products.count
  end

  private

  def count_active_products
    Product.where(status: 'active').count
  end

  def calculate_revenue_by_category
    Product.where(status: 'active')
           .joins(:category, :order_items)
           .where(order_items: { created_at: @date_range })
           .group('categories.name')
           .sum('order_items.quantity * order_items.price')
  end

  def find_top_performers
    Product.where(status: 'active')
           .joins(:order_items)
           .where(order_items: { created_at: @date_range })
           .group(:id)
           .order('SUM(order_items.quantity * order_items.price) DESC')
           .limit(10)
           .pluck(:name, 'SUM(order_items.quantity * order_items.price)')
  end

  def check_inventory_levels
    low_stock = Product.where(status: 'active').where('stock_quantity < ?', 10)
    out_of_stock = Product.where(status: 'active').where(stock_quantity: 0)
    
    {
      low_stock_count: low_stock.count,
      out_of_stock_count: out_of_stock.count,
      low_stock_products: low_stock.pluck(:name, :stock_quantity)
    }
  end

  def calculate_conversion_rates
    active_products = Product.where(status: 'active').includes(:product_views, :order_items)
    
    total_views = active_products.sum { |p| p.product_views.where(created_at: @date_range).count }
    total_purchases = active_products.sum { |p| p.order_items.where(created_at: @date_range).count }
    
    {
      total_views: total_views,
      total_purchases: total_purchases,
      conversion_rate: total_views > 0 ? (total_purchases.to_f / total_views * 100).round(2) : 0
    }
  end

  def calculate_new_price(current_price, percentage_change)
    multiplier = 1 + (percentage_change / 100.0)
    (current_price * multiplier).round(2)
  end
end