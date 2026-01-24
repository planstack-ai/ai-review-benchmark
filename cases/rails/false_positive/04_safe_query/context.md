# 既存コードベース情報

## Product モデル

```ruby
class Product < ApplicationRecord
  scope :published, -> { where(published: true) }
  scope :search_by_name, ->(keyword) {
    where("name LIKE ?", "%#{sanitize_sql_like(keyword)}%")
  }
end
```
