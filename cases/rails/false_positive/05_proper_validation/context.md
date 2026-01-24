# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  validates :name, presence: true
  validates :email, presence: true,
                    format: { with: URI::MailTo::EMAIL_REGEXP },
                    uniqueness: { case_sensitive: false }
end
```

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "name", null: false
  t.string "email", null: false
  t.datetime "created_at", null: false
  t.index ["email"], name: "index_users_on_email", unique: true
end
```
