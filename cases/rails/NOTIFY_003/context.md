# 既存コードベース

## スキーマ

```ruby
# notifications table
# - id: bigint
# - user_id: bigint
# - notifiable_type: string
# - notifiable_id: bigint
# - sent_at: datetime
# - email_sent: boolean
```

## モデル・サービス

```ruby
class OrderMailer < ApplicationMailer
  def confirmation(order)
    @order = order
    @user = order.user
    mail(to: @user.email, subject: '注文確認')
  end
end

class NotificationService
  def self.send_once(user, notifiable)
    return if already_sent?(user, notifiable)
    # send notification
    mark_sent!(user, notifiable)
  end
end
```
