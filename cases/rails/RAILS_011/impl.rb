# frozen_string_literal: true

# 注文確定処理サービス
# 外側で注文を確定し、内側で通知ログを作成する
# 通知ログの作成に失敗しても、注文確定は成功させたい
class OrderConfirmer
  def initialize(order)
    @order = order
  end

  def call
    ActiveRecord::Base.transaction do
      @order.update!(status: :confirmed)
      @order.update!(confirmed_at: Time.current)

      # 通知ログ作成（失敗しても本体には影響させたくない）
      ActiveRecord::Base.transaction do
        create_notification_log!
      rescue StandardError => e
        Rails.logger.warn("Notification log failed: #{e.message}")
        raise ActiveRecord::Rollback
      end

      true
    end
  end

  private

  def create_notification_log!
    NotificationLog.create!(
      order_id: @order.id,
      event_type: 'order_confirmed',
      message: "Order #{@order.id} has been confirmed"
    )
  end
end