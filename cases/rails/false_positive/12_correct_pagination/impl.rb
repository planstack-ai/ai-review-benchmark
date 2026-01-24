# frozen_string_literal: true

class ProductListService
  PER_PAGE = 20

  def initialize(page:)
    @page = page
  end

  def fetch
    products = Product.published.page(@page).per(PER_PAGE)

    {
      products: products,
      pagination: {
        current_page: @page,
        total_pages: products.total_pages,
        total_count: products.total_count
      }
    }
  end
end
