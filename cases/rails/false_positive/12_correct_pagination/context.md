# 既存コードベース情報

## Product モデル

```ruby
class Product < ApplicationRecord
  # Kaminari でページネーション
  paginates_per 20

  scope :published, -> { where(published: true) }
end
```

## Kaminari

```ruby
# Kaminari のメソッド
# .page(n) - n ページ目を取得（1始まり）
# .per(n) - 1ページあたり n 件
# .total_pages - 総ページ数
# .total_count - 総レコード数
```
