# frozen_string_literal: true

class CacheWarmingService
  CACHE_KEYS = %w[
    homepage_featured
    navigation_menu
    popular_products
    category_products
  ].freeze

  BATCH_SIZE = 100
  TIMEOUT_SECONDS = 30

  def initialize(logger: Rails.logger)
    @logger = logger
    @warmed_keys = []
    @failed_keys = []
    @job = nil
  end

  def call
    @job = create_warming_job
    @job.mark_as_running!

    @logger.info "Starting cache warming process for #{CACHE_KEYS.size} keys"
    start_time = Time.current

    CACHE_KEYS.each do |cache_key|
      warm_cache_key(cache_key)
    end

    log_completion_stats(start_time)
    complete_job
    build_result
  rescue StandardError => e
    @job&.mark_as_failed!(e)
    raise
  end

  private

  attr_reader :logger, :warmed_keys, :failed_keys

  def create_warming_job
    CacheWarmingJob.create!(
      job_type: 'homepage',
      status: 'pending'
    )
  end

  def complete_job
    if failed_keys.empty?
      @job.mark_as_completed!
    else
      @job.mark_as_failed!("Failed keys: #{failed_keys.join(', ')}")
    end
  end

  def warm_cache_key(cache_key)
    case cache_key
    when 'homepage_featured'
      warm_homepage_featured
    when 'navigation_menu'
      warm_navigation_menu
    when 'popular_products'
      warm_popular_products
    when 'category_products'
      warm_category_products
    end

    warmed_keys << cache_key
    logger.debug "Successfully warmed cache for: #{cache_key}"
  rescue StandardError => e
    failed_keys << cache_key
    logger.error "Failed to warm cache for #{cache_key}: #{e.message}"
  end

  def warm_homepage_featured
    Product.homepage_featured
  end

  def warm_navigation_menu
    Category.navigation_menu
  end

  def warm_popular_products
    Rails.cache.fetch('products/popular', expires_in: 1.hour) do
      Product.popular.includes(:category).to_a
    end
  end

  def warm_category_products
    Category.active.root_categories.each do |category|
      Product.by_category_cached(category.slug)
      category.product_count
    end
  end

  def log_completion_stats(start_time)
    duration = Time.current - start_time
    logger.info "Cache warming completed in #{duration.round(2)}s"
    logger.info "Successfully warmed: #{warmed_keys.size} keys"
    logger.info "Failed to warm: #{failed_keys.size} keys" if failed_keys.any?
  end

  def build_result
    {
      success: failed_keys.empty?,
      warmed_count: warmed_keys.size,
      failed_count: failed_keys.size,
      failed_keys: failed_keys,
      job_id: @job&.id
    }
  end
end
