# 既存コードベース情報

## Article モデル

```ruby
class Article < ApplicationRecord
  belongs_to :author, class_name: 'User'
  has_many :comments

  scope :published, -> { where.not(published_at: nil).where('published_at <= ?', Time.current) }
  scope :draft, -> { where(published_at: nil) }
  scope :newest_first, -> { order(published_at: :desc) }
  scope :oldest_first, -> { order(published_at: :asc) }

  def published?
    published_at.present? && published_at <= Time.current
  end
end
```

## スキーマ情報

```ruby
# articles テーブル
# - title: string
# - body: text
# - author_id: integer
# - published_at: datetime (公開日時、nilなら下書き)
# - created_at: datetime
```
