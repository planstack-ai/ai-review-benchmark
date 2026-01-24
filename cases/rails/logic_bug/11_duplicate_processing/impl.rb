# frozen_string_literal: true

class PointGrantService
  def initialize(order)
    @order = order
  end

  def execute
    return 0 if @order.points_granted?

    points = calculate_points
    grant_points(points)
    # BUG: mark_points_granted! is called AFTER returning
    # This line is unreachable, so points_granted? will always be false
    # and points will be granted multiple times on retry
    points
    @order.mark_points_granted!
  end

  private

  def calculate_points
    @order.calculate_points
  end

  def grant_points(points)
    @order.user.add_points(points)
  end
end
