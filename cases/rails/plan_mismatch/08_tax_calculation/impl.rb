# frozen_string_literal: true

class InvoiceGenerator
  TAX_RATE = 0.1

  def initialize(order)
    @order = order
  end

  def generate
    {
      order_id: @order.id,
      items: generate_items,
      subtotal: @order.subtotal,
      tax: calculate_tax,
      total: calculate_total
    }
  end

  private

  def generate_items
    @order.order_items.map do |item|
      {
        name: item.product.name,
        quantity: item.quantity,
        unit_price: item.product.price,  # 税抜価格のまま表示（これは正しい）
        line_total: item.line_total       # 税抜小計（これも正しい）
      }
    end
  end

  def calculate_tax
    (@order.subtotal * TAX_RATE).floor
  end

  def calculate_total
    # BUG: 税抜のsubtotalをそのまま使っている。税込にすべき
    @order.subtotal + calculate_tax  # この実装自体は正しいが...
  end
end

# 実際のバグは別の場所に：
# BUG: TaxCalculator.tax_included_priceを使わず独自実装している
# また、定数もTaxCalculator::TAX_RATEを使うべき
