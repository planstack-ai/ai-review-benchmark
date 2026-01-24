# frozen_string_literal: true

class WelcomeEmailJob < ApplicationJob
  queue_as :mailers

  retry_on StandardError, wait: :polynomially_longer, attempts: 3

  def perform(user_id)
    user = User.find_by(id: user_id)
    return if user.nil?  # ユーザーが削除された場合はスキップ

    NotificationMailer.welcome(user).deliver_now
  end
end
