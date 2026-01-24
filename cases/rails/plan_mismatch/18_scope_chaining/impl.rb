# frozen_string_literal: true

class ProductSearchService
  def initialize(min_price:, max_price:)
    @min_price = min_price
    @max_price = max_price
  end

  def search
    # BUG: in_stock が欠落、oldest_first を使用（newest_first が正しい）
    Product.published
           .price_between(@min_price, @max_price)
           .oldest_first
  end
end
