# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: products
#
#  id           :bigint           not null, primary key
#  name         :string           not null
#  description  :text
#  price        :decimal(10,2)    not null
#  category_id  :bigint           not null
#  featured     :boolean          default(false)
#  active       :boolean          default(true)
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: categories
#
#  id           :bigint           not null, primary key
#  name         :string           not null
#  slug         :string           not null
#  parent_id    :bigint
#  position     :integer          default(0)
#  active       :boolean          default(true)
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: cache_warming_jobs
#
#  id           :bigint           not null, primary key
#  job_type     :string           not null
#  status       :string           default('pending')
#  started_at   :datetime
#  completed_at :datetime
#  error_message :text
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
```

## Models

```ruby
class Product < ApplicationRecord
  belongs_to :category
  
  scope :active, -> { where(active: true) }
  scope :featured, -> { where(featured: true) }
  scope :by_category, ->(category) { where(category: category) }
  scope :popular, -> { order(created_at: :desc).limit(20) }
  
  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
  
  def cache_key_with_version
    "#{cache_key}-#{cache_version}"
  end
  
  def self.homepage_featured
    Rails.cache.fetch("products/homepage_featured", expires_in: 1.hour) do
      featured.active.includes(:category).limit(8).to_a
    end
  end
  
  def self.by_category_cached(category_slug)
    Rails.cache.fetch("products/category/#{category_slug}", expires_in: 30.minutes) do
      joins(:category)
        .where(categories: { slug: category_slug, active: true })
        .active
        .includes(:category)
        .order(:name)
        .to_a
    end
  end
end

class Category < ApplicationRecord
  has_many :products, dependent: :destroy
  has_many :subcategories, class_name: 'Category', foreign_key: 'parent_id'
  belongs_to :parent, class_name: 'Category', optional: true
  
  scope :active, -> { where(active: true) }
  scope :root_categories, -> { where(parent_id: nil) }
  scope :ordered, -> { order(:position, :name) }
  
  validates :name, presence: true
  validates :slug, presence: true, uniqueness: true
  
  def self.navigation_menu
    Rails.cache.fetch("categories/navigation", expires_in: 2.hours) do
      root_categories.active.ordered.includes(:subcategories).to_a
    end
  end
  
  def product_count
    Rails.cache.fetch("categories/#{id}/product_count", expires_in: 1.hour) do
      products.active.count
    end
  end
end

class CacheWarmingJob < ApplicationRecord
  VALID_STATUSES = %w[pending running completed failed].freeze
  VALID_JOB_TYPES = %w[products categories navigation homepage].freeze
  
  validates :job_type, inclusion: { in: VALID_JOB_TYPES }
  validates :status, inclusion: { in: VALID_STATUSES }
  
  scope :pending, -> { where(status: 'pending') }
  scope :running, -> { where(status: 'running') }
  scope :completed, -> { where(status: 'completed') }
  scope :failed, -> { where(status: 'failed') }
  scope :recent, -> { order(created_at: :desc) }
  
  def mark_as_running!
    update!(status: 'running', started_at: Time.current)
  end
  
  def mark_as_completed!
    update!(status: 'completed', completed_at: Time.current)
  end
  
  def mark_as_failed!(error)
    update!(status: 'failed', error_message: error.to_s, completed_at: Time.current)
  end
  
  def duration
    return nil unless started_at && completed_at
    completed_at - started_at
  end
end
```