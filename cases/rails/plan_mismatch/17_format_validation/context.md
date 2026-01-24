# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  # ハイフンあり形式: 090-1234-5678
  PHONE_FORMAT = /\A\d{2,4}-\d{2,4}-\d{4}\z/

  validates :phone_number, format: { with: PHONE_FORMAT }, allow_blank: true
end
```

## PhoneFormatter

```ruby
module PhoneFormatter
  # 電話番号をハイフンあり形式に正規化
  # "09012345678" -> "090-1234-5678"
  # "090-1234-5678" -> "090-1234-5678"（そのまま）
  def self.normalize(number)
    return nil if number.blank?

    digits = number.gsub(/\D/, "")
    case digits.length
    when 10
      "#{digits[0..1]}-#{digits[2..5]}-#{digits[6..9]}"
    when 11
      "#{digits[0..2]}-#{digits[3..6]}-#{digits[7..10]}"
    else
      number  # 形式が不明な場合はそのまま
    end
  end

  # ハイフンを除去
  def self.strip_hyphens(number)
    number&.gsub(/-/, "")
  end
end
```

## スキーマ

```ruby
create_table "users", force: :cascade do |t|
  t.string "name", null: false
  t.string "phone_number"
end
```
