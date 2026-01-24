# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  has_secure_password
  enum role: { user: 0, admin: 1 }

  # 公開可能な属性
  PUBLIC_ATTRIBUTES = %i[id name created_at].freeze

  # 機密属性
  # email - プライバシー
  # password_digest - セキュリティ
  # role - 内部情報
end
```

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "name", null: false
  t.string "email", null: false
  t.string "password_digest", null: false
  t.integer "role", default: 0
  t.datetime "created_at", null: false
end
```
