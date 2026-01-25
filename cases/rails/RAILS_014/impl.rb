# frozen_string_literal: true

# Admin product management service
# Provides methods to list products including inactive ones
class AdminProductService
  # List all products for admin management
  def all_products
    Product.unscoped.recently_updated
  end

  # List all featured products including inactive
  # Used for managing featured product rotation
  def all_featured_products
    Product.unscoped.featured
  end

  # List all inactive products for review
  def inactive_products
    Product.unscoped.where(active: false).recently_updated
  end

  # List products by category including inactive
  def products_by_category(category_id)
    Product.unscoped.in_category(category_id).recently_updated
  end

  # Count all products by status
  def product_counts
    {
      total: Product.unscoped.count,
      active: Product.unscoped.where(active: true).count,
      inactive: Product.unscoped.where(active: false).count,
      featured: Product.unscoped.featured.count
    }
  end
end
