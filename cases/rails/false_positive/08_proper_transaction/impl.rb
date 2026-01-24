# frozen_string_literal: true

class PointExchangeService
  def initialize(user:, product:, points:)
    @user = user
    @product = product
    @points = points
  end

  def execute
    ActiveRecord::Base.transaction do
      @user.deduct_points(@points)
      Exchange.create!(
        user: @user,
        product: @product,
        points_used: @points
      )
    end
  end
end
