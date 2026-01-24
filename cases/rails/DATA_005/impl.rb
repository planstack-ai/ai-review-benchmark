# frozen_string_literal: true

class OrderHistoryService
  def initialize(order)
    @order = order
    @order_items = order.order_items.includes(:product)
  end

  def generate_order_summary
    {
      order_id: @order.id,
      order_date: @order.created_at,
      customer_name: @order.customer.full_name,
      items: build_item_summaries,
      total_amount: calculate_total_amount,
      status: @order.status
    }
  end

  def export_to_csv
    CSV.generate(headers: true) do |csv|
      csv << csv_headers
      @order_items.each do |item|
        csv << build_csv_row(item)
      end
    end
  end

  def generate_invoice_data
    {
      invoice_number: generate_invoice_number,
      billing_address: @order.billing_address,
      shipping_address: @order.shipping_address,
      line_items: build_detailed_line_items,
      subtotal: calculate_subtotal,
      tax_amount: calculate_tax_amount,
      shipping_cost: @order.shipping_cost,
      total: calculate_total_amount
    }
  end

  private

  def build_item_summaries
    @order_items.map do |item|
      {
        product_name: item.product.name,
        quantity: item.quantity,
        unit_price: item.unit_price,
        total_price: item.quantity * item.unit_price,
        sku: item.product.sku
      }
    end
  end

  def build_detailed_line_items
    @order_items.map do |item|
      {
        description: item.product.name,
        quantity: item.quantity,
        unit_price: format_currency(item.unit_price),
        line_total: format_currency(item.quantity * item.unit_price),
        product_code: item.product.sku,
        category: item.product.category&.name
      }
    end
  end

  def build_csv_row(item)
    [
      @order.id,
      @order.created_at.strftime('%Y-%m-%d'),
      item.product.name,
      item.quantity,
      item.unit_price,
      item.quantity * item.unit_price
    ]
  end

  def csv_headers
    ['Order ID', 'Order Date', 'Product Name', 'Quantity', 'Unit Price', 'Total Price']
  end

  def calculate_total_amount
    @order_items.sum { |item| item.quantity * item.unit_price } + 
    @order.shipping_cost + 
    calculate_tax_amount
  end

  def calculate_subtotal
    @order_items.sum { |item| item.quantity * item.unit_price }
  end

  def calculate_tax_amount
    calculate_subtotal * @order.tax_rate
  end

  def generate_invoice_number
    "INV-#{@order.id.to_s.rjust(6, '0')}-#{Date.current.strftime('%Y%m')}"
  end

  def format_currency(amount)
    sprintf('$%.2f', amount)
  end
end