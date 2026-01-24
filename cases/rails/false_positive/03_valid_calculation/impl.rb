# frozen_string_literal: true

class PriceService
  def initialize(product)
    @product = product
  end

  def price_with_tax
    TaxCalculator.with_tax(@product.price)
  end
end
