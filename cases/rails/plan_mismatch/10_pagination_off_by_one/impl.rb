# frozen_string_literal: true

class ProductListService
  PER_PAGE = 20

  def initialize(page)
    @page = page || 1
  end

  def execute
    {
      products: fetch_products,
      current_page: @page,
      total_pages: calculate_total_pages
    }
  end

  private

  def fetch_products
    # BUG: 0始まりのoffset計算をしている。Kaminariのpageメソッドを使うべき
    offset = @page * PER_PAGE  # 1ページ目でoffset=20になってしまう（正しくは0）
    Product.visible.limit(PER_PAGE).offset(offset)
  end

  def calculate_total_pages
    (Product.visible.count.to_f / PER_PAGE).ceil
  end
end
