# frozen_string_literal: true

class ProductCreationService
  def initialize(params)
    @params = params
  end

  def execute
    # BUG: デフォルト値が仕様と異なる
    # stock は 0、published は false が正しい
    Product.create!(
      name: @params[:name],
      price: @params[:price],
      stock: @params[:stock] || 1,        # BUG: should be 0
      published: @params[:published] || true  # BUG: should be false
    )
  end
end
