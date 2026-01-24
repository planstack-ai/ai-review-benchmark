# frozen_string_literal: true

class ProfileSerializer
  def initialize(user)
    @user = user
  end

  def to_hash
    {
      name: @user.display_name,
      bio: @user.profile.bio,  # BUG: profileがnilの場合NoMethodError。bio_or_defaultを使うべき
      address: format_address
    }
  end

  private

  def format_address
    @user.profile.address || '未設定'  # BUG: profileがnilの場合NoMethodError
  end
end
