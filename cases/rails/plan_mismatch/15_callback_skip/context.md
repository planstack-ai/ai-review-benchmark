# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  attr_accessor :skip_notification_callback

  validates :name, presence: true
  validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }

  after_update :send_update_notification, unless: :skip_notification_callback

  private

  def send_update_notification
    UserMailer.profile_updated(self).deliver_later
  end
end
```

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "name", null: false
  t.string "email", null: false
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
end
```
