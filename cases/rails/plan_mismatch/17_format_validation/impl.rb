# frozen_string_literal: true

class PhoneRegistrationService
  def initialize(user, phone_number)
    @user = user
    @phone_number = phone_number
  end

  def execute
    # BUG: strip_hyphens はハイフンを除去する（逆の処理）
    # normalize を使うべき
    normalized = PhoneFormatter.strip_hyphens(@phone_number)
    @user.update!(phone_number: normalized)
  end
end
