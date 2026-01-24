# 既存コードベース情報

## Product モデル（Kaminariを使用）

```ruby
class Product < ApplicationRecord
  paginates_per 20

  scope :visible, -> { where(visible: true) }
  scope :in_stock, -> { where('stock > 0') }

  # Kaminari による page スコープ（1始まり）
  # Product.page(1) -> 1-20件目
  # Product.page(2) -> 21-40件目

  def self.per_page
    20
  end

  def self.total_pages
    (visible.count.to_f / per_page).ceil
  end
end
```

## Kaminari の動作

```ruby
# Kaminariのpageメソッドは1始まり
# page(1) = OFFSET 0
# page(2) = OFFSET 20
# page(0) や page(nil) は page(1) と同じ扱い
```
