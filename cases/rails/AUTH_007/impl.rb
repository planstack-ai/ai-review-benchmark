# frozen_string_literal: true

class CouponRedemptionService
  include ActiveModel::Model

  attr_accessor :user, :coupon_code, :order_total

  validates :user, presence: true
  validates :coupon_code, presence: true
  validates :order_total, presence: true, numericality: { greater_than: 0 }

  def initialize(user:, coupon_code:, order_total:)
    @user = user
    @coupon_code = coupon_code.to_s.strip.upcase
    @order_total = order_total.to_f
    @errors = []
  end

  def call
    return failure_result unless valid?

    coupon = find_coupon
    return failure_result('Invalid coupon code') unless coupon

    return failure_result('Coupon has expired') if coupon_expired?(coupon)
    return failure_result('Coupon usage limit exceeded') if usage_limit_exceeded?(coupon)
    return failure_result('Order does not meet minimum amount') unless meets_minimum_amount?(coupon)

    discount_amount = calculate_discount(coupon)
    return failure_result('Discount cannot be applied') if discount_amount <= 0

    create_coupon_usage(coupon, discount_amount)
    success_result(coupon, discount_amount)
  end

  private

  def find_coupon
    Coupon.find_by(code: @coupon_code)
  end

  def coupon_expired?(coupon)
    return false unless coupon.expires_at
    coupon.expires_at < Time.current
  end

  def usage_limit_exceeded?(coupon)
    return false unless coupon.usage_limit
    coupon.coupon_usages.count >= coupon.usage_limit
  end

  def meets_minimum_amount?(coupon)
    return true unless coupon.minimum_order_amount
    @order_total >= coupon.minimum_order_amount
  end

  def calculate_discount(coupon)
    case coupon.discount_type
    when 'percentage'
      discount = (@order_total * coupon.discount_value / 100.0)
      coupon.max_discount_amount ? [discount, coupon.max_discount_amount].min : discount
    when 'fixed_amount'
      [coupon.discount_value, @order_total].min
    else
      0
    end
  end

  def create_coupon_usage(coupon, discount_amount)
    CouponUsage.create!(
      coupon: coupon,
      user: @user,
      discount_amount: discount_amount,
      order_total: @order_total,
      used_at: Time.current
    )
  end

  def success_result(coupon, discount_amount)
    OpenStruct.new(
      success: true,
      coupon: coupon,
      discount_amount: discount_amount,
      final_total: @order_total - discount_amount,
      message: 'Coupon applied successfully'
    )
  end

  def failure_result(message = 'Invalid request')
    @errors << message
    OpenStruct.new(
      success: false,
      coupon: nil,
      discount_amount: 0,
      final_total: @order_total,
      message: message,
      errors: @errors
    )
  end
end