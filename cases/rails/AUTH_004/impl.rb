# frozen_string_literal: true

class ProductPriceUpdateService
  include ActiveModel::Model
  include ActiveModel::Attributes

  attribute :product_id, :integer
  attribute :new_price, :decimal, precision: 8, scale: 2
  attribute :current_user
  attribute :reason, :string

  validates :product_id, presence: true
  validates :new_price, presence: true, numericality: { greater_than: 0 }
  validates :current_user, presence: true
  validates :reason, presence: true, length: { minimum: 10, maximum: 500 }

  def initialize(attributes = {})
    super
    @errors_occurred = []
    @price_history = []
  end

  def call
    return failure_result unless valid?
    return failure_result unless product_exists?
    return failure_result unless price_changed?

    ActiveRecord::Base.transaction do
      update_product_price
      create_price_history_record
      notify_stakeholders
    end

    success_result
  rescue StandardError => e
    @errors_occurred << "Price update failed: #{e.message}"
    failure_result
  end

  private

  def product_exists?
    return true if product.present?

    @errors_occurred << "Product not found"
    false
  end

  def price_changed?
    return true unless new_price == product.price

    @errors_occurred << "New price must be different from current price"
    false
  end

  def update_product_price
    product.update!(
      price: new_price,
      price_updated_at: Time.current,
      price_updated_by: current_user.id
    )
  end

  def create_price_history_record
    @price_history << PriceHistory.create!(
      product: product,
      old_price: product.price_was,
      new_price: new_price,
      changed_by: current_user,
      reason: reason,
      changed_at: Time.current
    )
  end

  def notify_stakeholders
    return unless significant_price_change?

    ProductPriceChangeNotificationJob.perform_later(
      product_id: product.id,
      old_price: product.price_was,
      new_price: new_price,
      changed_by_user_id: current_user.id
    )
  end

  def significant_price_change?
    return false unless product.price_was.present?

    percentage_change = ((new_price - product.price_was) / product.price_was * 100).abs
    percentage_change >= 10.0
  end

  def product
    @product ||= Product.find_by(id: product_id)
  end

  def success_result
    {
      success: true,
      product: product.reload,
      price_history: @price_history.last,
      message: "Price updated successfully from #{product.price_was} to #{new_price}"
    }
  end

  def failure_result
    {
      success: false,
      errors: @errors_occurred + errors.full_messages,
      product: product
    }
  end
end