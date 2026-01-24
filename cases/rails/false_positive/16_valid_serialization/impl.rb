# frozen_string_literal: true

class UserSerializer
  def initialize(user)
    @user = user
  end

  def as_json
    {
      id: @user.id,
      name: @user.name,
      created_at: @user.created_at.iso8601
    }
  end
end
