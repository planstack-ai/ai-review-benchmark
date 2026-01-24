# frozen_string_literal: true

class EmailNotificationService
  def initialize(user, message)
    @user = user
    @message = message
  end

  def send
    # BUG: Missing 'return' keyword - this only evaluates the condition
    # but doesn't actually return from the method
    false unless @user.email_notifications_enabled?
    false unless @user.email_verified?

    deliver_email
    true
  end

  private

  def deliver_email
    NotificationMailer.send_notification(@user, @message).deliver_later
  end
end
