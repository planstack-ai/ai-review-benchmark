# frozen_string_literal: true

class ProductSearchService
  def initialize(keyword)
    @keyword = keyword
  end

  def search
    # BUG: SQL インジェクション脆弱性
    # ユーザー入力を直接文字列補間している
    Product.where("name LIKE '%#{@keyword}%'")
  end
end
