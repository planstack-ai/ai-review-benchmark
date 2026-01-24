# frozen_string_literal: true

class CouponApplicationService
  attr_reader :order, :coupon, :errors

  def initialize(order, coupon)
    @order = order
    @coupon = coupon
    @errors = []
  end

  def call
    return failure('Order not found') unless order
    return failure('Coupon not found') unless coupon
    return failure('Coupon is not active') unless coupon_active?
    return failure('Coupon has expired') if coupon_expired?
    return failure('Order does not meet minimum requirements') unless meets_minimum_requirements?
    return failure('Coupon usage limit exceeded') if usage_limit_exceeded?

    apply_coupon_discount
    update_order_totals
    record_coupon_usage

    success
  end

  def success?
    errors.empty?
  end

  private

  def coupon_active?
    coupon.active?
  end

  def coupon_expired?
    coupon.expires_at && coupon.expires_at < Time.current
  end

  def meets_minimum_requirements?
    return true unless coupon.minimum_order_amount
    
    order.subtotal >= coupon.minimum_order_amount
  end

  def usage_limit_exceeded?
    return false unless coupon.usage_limit
    
    coupon.usage_count >= coupon.usage_limit
  end

  def apply_coupon_discount
    discount_amount = calculate_discount_amount
    
    order.coupon_discount = discount_amount
    order.applied_coupons << coupon
    order.save!
  end

  def calculate_discount_amount
    case coupon.discount_type
    when 'percentage'
      (order.subtotal * coupon.discount_value / 100.0).round(2)
    when 'fixed_amount'
      [coupon.discount_value, order.subtotal].min
    else
      0.0
    end
  end

  def update_order_totals
    order.total = order.subtotal - order.coupon_discount + order.tax_amount + order.shipping_amount
    order.save!
  end

  def record_coupon_usage
    coupon.increment!(:usage_count)
    
    CouponUsage.create!(
      coupon: coupon,
      order: order,
      discount_amount: order.coupon_discount,
      used_at: Time.current
    )
  end

  def success
    OpenStruct.new(success?: true, errors: [])
  end

  def failure(message)
    @errors << message
    OpenStruct.new(success?: false, errors: errors)
  end
end