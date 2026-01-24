# 既存コードベース情報

## CsvParser

```ruby
module CsvParser
  def self.parse(file)
    CSV.read(file, headers: true).map(&:to_h)
  end
end
```

## Product モデル

```ruby
class Product < ApplicationRecord
  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
end
```

## 期待される戻り値形式

```ruby
{
  success: 10,  # 成功件数
  failed: 2     # 失敗件数
}
```
