# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  has_secure_password

  def self.authenticate(email, password)
    user = find_by(email: email)
    user&.authenticate(password) ? user : nil
  end
end
```

## セッション管理

```ruby
# ログイン時のベストプラクティス
# 1. reset_session でセッションIDを再生成
# 2. session[:user_id] にユーザーIDを保存
```

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "email", null: false
  t.string "password_digest", null: false
end
```
