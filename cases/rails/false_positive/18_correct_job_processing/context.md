# 既存コードベース情報

## ApplicationJob

```ruby
class ApplicationJob < ActiveJob::Base
  # 共通のリトライ設定は個別ジョブで上書き可能
end
```

## NotificationMailer

```ruby
class NotificationMailer < ApplicationMailer
  def welcome(user)
    @user = user
    mail(to: user.email, subject: "ようこそ")
  end
end
```
