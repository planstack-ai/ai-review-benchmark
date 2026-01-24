# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  has_one :profile, dependent: :destroy

  delegate :bio, :address, to: :profile, allow_nil: true

  # 表示名を取得（nickname優先）
  def display_name
    nickname.presence || full_name
  end

  # 自己紹介文を取得（未設定なら空文字）
  def bio_or_default
    bio.presence || ''
  end

  def full_name
    "#{last_name} #{first_name}"
  end
end
```

## Profile モデル

```ruby
class Profile < ApplicationRecord
  belongs_to :user

  # すべてのカラムは任意
  # - bio: text (自己紹介)
  # - address: string (住所)
  # - website: string (Webサイト)
end
```

## スキーマ情報

```ruby
# users テーブル
# - nickname: string (任意)
# - first_name: string
# - last_name: string

# profiles テーブル
# - user_id: integer
# - bio: text (任意)
# - address: string (任意)
```
