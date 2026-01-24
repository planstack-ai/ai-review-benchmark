# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  has_one_attached :avatar

  validates :avatar,
    content_type: %w[image/jpeg image/png image/gif],
    size: { less_than: 5.megabytes }
end
```

## ActiveStorage

```ruby
# ActiveStorage は自動的に:
# - ファイル名をサニタイズ
# - ユニークなキーでBlobを保存
# - Content-Typeを検証（設定時）
```
