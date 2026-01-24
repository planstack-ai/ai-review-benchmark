# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  # timezone: string (例: "Asia/Tokyo", "America/New_York")

  def timezone
    super || "UTC"
  end
end
```

## Event モデル

```ruby
class Event < ApplicationRecord
  # starts_at: datetime (UTCで保存)
  belongs_to :organizer, class_name: "User"
  has_many :participants, through: :event_participations, source: :user
end
```

## TimeFormatter

```ruby
module TimeFormatter
  def self.format(time, format_string)
    time.strftime(format_string)
  end

  FORMATS = {
    japanese: "%Y年%m月%d日 %H:%M",
    iso: "%Y-%m-%dT%H:%M:%S%z"
  }.freeze
end
```

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "name"
  t.string "timezone", default: "UTC"
end

create_table "events", force: :cascade do |t|
  t.string "title"
  t.datetime "starts_at", null: false
  t.bigint "organizer_id", null: false
end
```
