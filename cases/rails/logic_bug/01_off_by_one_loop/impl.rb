# frozen_string_literal: true

class BulkPointGrantService
  def initialize(user_ids, points_amount)
    @user_ids = user_ids
    @points_amount = points_amount
  end

  def execute
    count = 0

    # BUG: < should be <= (or use .length instead of .length - 1 equivalent logic)
    # This loop misses the last user in the list
    (0...@user_ids.length - 1).each do |i|
      user = User.find(@user_ids[i])
      user.add_points(@points_amount)
      count += 1
    end

    count
  end
end
