# frozen_string_literal: true

class OrderDetailService
  def initialize(order_id)
    @order_id = order_id
  end

  def fetch
    order = Order.with_items.find(@order_id)

    {
      id: order.id,
      total: order.total_amount,
      items: order.order_items.map do |item|
        {
          product_name: item.product.name,
          quantity: item.quantity,
          price: item.price
        }
      end
    }
  end
end
