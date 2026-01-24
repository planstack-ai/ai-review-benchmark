# 既存コードベース情報

## Article モデル

```ruby
class Article < ApplicationRecord
  belongs_to :author, class_name: "User"

  scope :published, -> { where(published: true) }
  scope :with_author, -> { includes(:author) }
end
```

## User モデル

```ruby
class User < ApplicationRecord
  has_many :articles, foreign_key: :author_id
end
```

## スキーマ

```ruby
create_table "articles", force: :cascade do |t|
  t.string "title", null: false
  t.text "body"
  t.bigint "author_id", null: false
  t.boolean "published", default: false
  t.datetime "created_at", null: false
end

create_table "users", force: :cascade do |t|
  t.string "name", null: false
end
```
