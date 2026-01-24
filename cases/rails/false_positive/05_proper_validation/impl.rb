# frozen_string_literal: true

class UserRegistrationService
  def initialize(params)
    @params = params
  end

  def execute
    user = User.new(@params.slice(:name, :email))

    if user.save
      { success: true, user: user }
    else
      { success: false, errors: user.errors.full_messages }
    end
  end
end
