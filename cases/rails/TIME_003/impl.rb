# frozen_string_literal: true

class CouponValidationService
  attr_reader :coupon, :user, :order

  def initialize(coupon:, user: nil, order: nil)
    @coupon = coupon
    @user = user
    @order = order
  end

  def call
    return validation_result(false, 'Coupon not found') unless coupon

    return validation_result(false, 'Coupon is not active') unless coupon_active?
    return validation_result(false, 'Coupon has expired') unless coupon_valid?
    return validation_result(false, 'Usage limit exceeded') unless usage_limit_valid?
    return validation_result(false, 'User not eligible') unless user_eligible?
    return validation_result(false, 'Order does not meet minimum requirements') unless order_requirements_met?

    validation_result(true, 'Coupon is valid')
  end

  def valid?
    call.success?
  end

  private

  def coupon_active?
    coupon.active?
  end

  def coupon_valid?
    return true unless coupon.expires_at

    Time.current < coupon.expires_at
  end

  def usage_limit_valid?
    return true unless coupon.usage_limit

    coupon.usage_count < coupon.usage_limit
  end

  def user_eligible?
    return true unless user
    return true unless coupon.user_restrictions?

    case coupon.user_restriction_type
    when 'first_time_only'
      user.orders.completed.empty?
    when 'returning_customers_only'
      user.orders.completed.any?
    when 'specific_users'
      coupon.eligible_user_ids.include?(user.id)
    else
      true
    end
  end

  def order_requirements_met?
    return true unless order
    return true unless coupon.minimum_order_amount

    order.subtotal >= coupon.minimum_order_amount
  end

  def validation_result(success, message)
    OpenStruct.new(success?: success, message: message, coupon: coupon)
  end
end