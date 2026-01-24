# frozen_string_literal: true

class AuthenticationService
  GENERIC_ERROR = "メールアドレスまたはパスワードが正しくありません"

  def initialize(email:, password:)
    @email = email
    @password = password
  end

  def authenticate
    user = User.find_by(email: @email.downcase)

    if user&.authenticate(@password)
      { success: true, user: user }
    else
      { success: false, error: GENERIC_ERROR }
    end
  end
end
