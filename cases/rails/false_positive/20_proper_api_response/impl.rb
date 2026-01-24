# frozen_string_literal: true

class Api::ProductsController < ApplicationController
  def show
    product = Product.find_by(id: params[:id])

    if product
      render **ApiResponse.success(serialize(product))
    else
      render **ApiResponse.not_found("商品が見つかりません")
    end
  end

  def create
    product = Product.new(product_params)

    if product.save
      render **ApiResponse.created(serialize(product))
    else
      render **ApiResponse.error(product.errors.full_messages.join(", "), status: :unprocessable_entity)
    end
  end

  private

  def product_params
    params.require(:product).permit(:name, :price, :description)
  end

  def serialize(product)
    {
      id: product.id,
      name: product.name,
      price: product.price
    }
  end
end
