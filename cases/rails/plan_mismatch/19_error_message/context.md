# 既存コードベース情報

## ErrorCode 定数

```ruby
module ErrorCode
  INVALID_PARAMS = "E001"
  NOT_FOUND = "E002"
  UNAUTHORIZED = "E003"
  FORBIDDEN = "E004"
  INTERNAL_ERROR = "E500"

  MESSAGES = {
    "E001" => "パラメータが不正です",
    "E002" => "リソースが見つかりません",
    "E003" => "認証が必要です",
    "E004" => "権限がありません",
    "E500" => "内部エラーが発生しました"
  }.freeze

  def self.message_for(code)
    MESSAGES[code] || "不明なエラー"
  end
end
```

## HTTP ステータス対応

| エラーコード | HTTPステータス |
|--------------|----------------|
| E001 | 400 |
| E002 | 404 |
| E003 | 401 |
| E004 | 403 |
| E500 | 500 |
