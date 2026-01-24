# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  def age
    return nil unless birthday

    today = Date.current
    age = today.year - birthday.year
    age -= 1 if today < birthday + age.years
    age
  end
end
```

## 年齢層の定義（ビジネス要件より）

| 年齢層 | 年齢範囲 | 説明 |
|--------|----------|------|
| child  | 0-12歳   | 小学生以下 |
| teen   | 13-19歳  | 中高生〜10代 |
| adult  | 20-64歳  | 成人〜現役世代 |
| senior | 65歳以上 | 高齢者 |

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "name", null: false
  t.date "birthday"
  t.datetime "created_at", null: false
  t.datetime "updated_at", null: false
end
```
