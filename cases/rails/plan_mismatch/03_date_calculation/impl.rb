# frozen_string_literal: true

class ExpirationNotificationService
  def notify_expiring_users
    expiring_subscriptions.each do |subscription|
      NotificationMailer.expiration_warning(subscription.user).deliver_later
      subscription.update!(notified_at: Time.current)
    end
  end

  private

  def expiring_subscriptions
    Subscription
      .where(notified_at: nil)
      .where('expires_at > ?', Time.current)
      .where('expires_at <= ?', 1.month.from_now)  # BUG: 30.days.from_now であるべき
  end
end
