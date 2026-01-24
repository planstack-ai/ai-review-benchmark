# frozen_string_literal: true

class CacheWarmingService
  CACHE_KEYS = %w[
    popular_products
    featured_categories
    user_preferences
    system_settings
    navigation_menu
  ].freeze

  BATCH_SIZE = 100
  TIMEOUT_SECONDS = 30

  def initialize(logger: Rails.logger)
    @logger = logger
    @warmed_keys = []
    @failed_keys = []
  end

  def call
    @logger.info "Starting cache warming process for #{CACHE_KEYS.size} keys"
    start_time = Time.current

    CACHE_KEYS.each do |cache_key|
      warm_cache_key(cache_key)
    end

    log_completion_stats(start_time)
    build_result
  end

  private

  attr_reader :logger, :warmed_keys, :failed_keys

  def warm_cache_key(cache_key)
    case cache_key
    when 'popular_products'
      warm_popular_products
    when 'featured_categories'
      warm_featured_categories
    when 'user_preferences'
      warm_user_preferences
    when 'system_settings'
      warm_system_settings
    when 'navigation_menu'
      warm_navigation_menu
    end

    warmed_keys << cache_key
    logger.debug "Successfully warmed cache for: #{cache_key}"
  rescue StandardError => e
    failed_keys << cache_key
    logger.error "Failed to warm cache for #{cache_key}: #{e.message}"
  end

  def warm_popular_products
    Rails.cache.fetch('popular_products', expires_in: 1.hour) do
      Product.popular.limit(50).includes(:category, :reviews).to_a
    end
  end

  def warm_featured_categories
    Rails.cache.fetch('featured_categories', expires_in: 2.hours) do
      Category.featured.includes(:products).order(:display_order).to_a
    end
  end

  def warm_user_preferences
    Rails.cache.fetch('user_preferences_defaults', expires_in: 4.hours) do
      UserPreference.default_settings
    end
  end

  def warm_system_settings
    Rails.cache.fetch('system_settings', expires_in: 6.hours) do
      Setting.active.pluck(:key, :value).to_h
    end
  end

  def warm_navigation_menu
    Rails.cache.fetch('navigation_menu', expires_in: 12.hours) do
      NavigationItem.published.includes(:children).order(:position).to_a
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
      failed_keys: failed_keys
    }
  end
end