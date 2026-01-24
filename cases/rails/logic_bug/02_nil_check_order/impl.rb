# frozen_string_literal: true

class UserProfileService
  def initialize(user_id)
    @user_id = user_id
  end

  def fetch
    user = User.find_by(id: @user_id)
    return nil unless user

    {
      name: user.full_name,
      email: user.email,
      # BUG: company.name is called before checking if company exists
      # This will raise NoMethodError when user.company is nil
      company_name: user.company.name || "個人"
    }
  end
end
