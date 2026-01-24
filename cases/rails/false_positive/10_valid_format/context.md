# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  def timezone
    super || "Asia/Tokyo"
  end
end
```

## I18n 設定

```ruby
# config/locales/ja.yml
ja:
  date:
    formats:
      default: "%Y年%m月%d日"
      long: "%Y年%m月%d日(%a)"
```
