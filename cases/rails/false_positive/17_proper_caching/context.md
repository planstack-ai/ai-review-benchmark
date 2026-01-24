# 既存コードベース情報

## Product モデル

```ruby
class Product < ApplicationRecord
  def cache_key_with_version
    "#{cache_key}/#{updated_at.to_i}"
  end
end
```

## Rails.cache

```ruby
# fetch: キャッシュがあれば返す、なければブロックを実行してキャッシュ
Rails.cache.fetch(key, expires_in: 1.hour) do
  # キャッシュがない場合に実行される
end
```
