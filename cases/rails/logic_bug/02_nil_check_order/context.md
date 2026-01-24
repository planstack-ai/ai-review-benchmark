# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  belongs_to :company, optional: true

  def full_name
    "#{last_name} #{first_name}"
  end
end
```

## Company モデル

```ruby
class Company < ApplicationRecord
  has_many :users

  def name
    company_name
  end
end
```

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "first_name", null: false
  t.string "last_name", null: false
  t.string "email", null: false
  t.bigint "company_id"  # nullable - 個人ユーザーは会社に所属しない
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
  t.index ["company_id"], name: "index_users_on_company_id"
end

create_table "companies", force: :cascade do |t|
  t.string "company_name", null: false
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
end
```
