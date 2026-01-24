# 既存コードベース情報

## Subscription モデル

```ruby
class Subscription < ApplicationRecord
  belongs_to :user

  # 指定日数以内に期限切れかどうか
  def expires_within?(days)
    !expired? && expires_at <= days.days.from_now
  end

  # 既に期限切れかどうか
  def expired?
    expires_at < Time.current
  end

  # 有効かどうか
  def active?
    !expired?
  end
end
```

## NotificationMailer

```ruby
class NotificationMailer < ApplicationMailer
  def expiration_warning(user)
    @user = user
    @subscription = user.subscription
    mail(to: user.email, subject: 'サブスクリプション期限のお知らせ')
  end
end
```

## スキーマ情報

```ruby
# subscriptions テーブル
# - user_id: integer
# - expires_at: datetime (有効期限)
# - notified_at: datetime (通知送信日時、未通知ならnil)
```
