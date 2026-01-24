# frozen_string_literal: true

class AgeGroupService
  def initialize(user)
    @user = user
  end

  def determine_group
    age = @user.age
    return nil if age.nil?

    # BUG: 境界値の処理が間違っている
    # 12歳は child であるべきだが、この実装では teen になる
    # 64歳は adult であるべきだが、この実装では senior になる
    if age <= 11
      "child"
    elsif age <= 19
      "teen"
    elsif age <= 63
      "adult"
    else
      "senior"
    end
  end
end
