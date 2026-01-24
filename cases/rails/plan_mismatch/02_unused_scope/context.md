# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  scope :active, -> { where(deleted_at: nil, suspended: false) }
  scope :recently_logged_in, ->(days) { where('last_login_at >= ?', days.days.ago) }
  scope :by_created_at, -> { order(created_at: :desc) }

  # 論理削除
  def soft_delete
    update!(deleted_at: Time.current)
  end

  # アカウント停止
  def suspend!
    update!(suspended: true)
  end
end
```

## スキーマ情報

```ruby
# users テーブル
# - deleted_at: datetime (論理削除フラグ)
# - suspended: boolean (停止フラグ)
# - last_login_at: datetime (最終ログイン日時)
# - created_at: datetime
```
