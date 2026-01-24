# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  scope :active, -> { where(deleted_at: nil, suspended: false) }
  scope :recently_logged_in, ->(days) { where("last_login_at >= ?", days.days.ago) }
  scope :by_created_at, -> { order(created_at: :desc) }
end
```

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "name", null: false
  t.datetime "deleted_at"
  t.boolean "suspended", default: false
  t.datetime "last_login_at"
  t.datetime "created_at", null: false
end
```
