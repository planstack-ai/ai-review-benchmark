# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  def email_notifications_enabled?
    notification_settings["email"] == true
  end

  def email_verified?
    email_verified_at.present?
  end
end
```

## NotificationMailer

```ruby
class NotificationMailer < ApplicationMailer
  def send_notification(user, message)
    @user = user
    @message = message
    mail(to: user.email, subject: "お知らせ")
  end
end
```

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "name", null: false
  t.string "email", null: false
  t.jsonb "notification_settings", default: {}, null: false
  t.datetime "email_verified_at"
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
end
```
