# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  enum role: { user: 0, moderator: 1, admin: 2 }

  validates :name, presence: true
  validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }

  def admin?
    role == "admin"
  end
end
```

## 許可されるパラメータ

プロフィール更新で許可されるパラメータ:
- `name` - 表示名
- `email` - メールアドレス

許可されないパラメータ:
- `role` - 権限（管理者のみ変更可能）
- `password_digest` - パスワード（別エンドポイント）

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "name", null: false
  t.string "email", null: false
  t.integer "role", default: 0, null: false
  t.string "password_digest"
end
```
