# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  has_many :orders, -> { order(created_at: :desc) }
  has_one :profile
  has_one :latest_order, -> { order(created_at: :desc) }, class_name: "Order"

  scope :active, -> { where(deleted_at: nil) }
  scope :with_latest_order, -> { includes(:latest_order) }
  scope :with_profile, -> { includes(:profile) }
  scope :with_associations, -> { with_latest_order.with_profile }

  def display_name
    profile&.display_name || name
  end
end
```

## Profile モデル

```ruby
class Profile < ApplicationRecord
  belongs_to :user

  validates :display_name, presence: true
end
```

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "name", null: false
  t.datetime "deleted_at"
end

create_table "profiles", force: :cascade do |t|
  t.bigint "user_id", null: false
  t.string "display_name"
  t.text "bio"
end

create_table "orders", force: :cascade do |t|
  t.bigint "user_id", null: false
  t.decimal "total_amount"
  t.datetime "created_at", null: false
end
```
