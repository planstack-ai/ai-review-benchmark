# frozen_string_literal: true

class AvatarUploadService
  ALLOWED_TYPES = %w[image/jpeg image/png image/gif].freeze
  MAX_SIZE = 5.megabytes

  def initialize(user, file)
    @user = user
    @file = file
  end

  def upload
    return { success: false, error: "ファイルがありません" } if @file.nil?
    return { success: false, error: "許可されていないファイル形式です" } unless valid_content_type?
    return { success: false, error: "ファイルサイズが大きすぎます" } unless valid_size?

    @user.avatar.attach(@file)

    if @user.save
      { success: true, url: Rails.application.routes.url_helpers.rails_blob_url(@user.avatar) }
    else
      { success: false, error: @user.errors.full_messages.join(", ") }
    end
  end

  private

  def valid_content_type?
    ALLOWED_TYPES.include?(@file.content_type)
  end

  def valid_size?
    @file.size <= MAX_SIZE
  end
end
