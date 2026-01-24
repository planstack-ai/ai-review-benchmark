# frozen_string_literal: true

class ProductCacheService
  CACHE_TTL = 1.hour

  def initialize(product_id)
    @product_id = product_id
  end

  def fetch
    Rails.cache.fetch(cache_key, expires_in: CACHE_TTL) do
      product = Product.find(@product_id)
      {
        id: product.id,
        name: product.name,
        price: product.price,
        updated_at: product.updated_at
      }
    end
  end

  private

  def cache_key
    "products/#{@product_id}"
  end
end
