# frozen_string_literal: true

class ProductSearchService
  def initialize(keyword)
    @keyword = keyword
  end

  def search
    Product.published.search_by_name(@keyword)
  end
end
