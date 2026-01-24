# 既存コードベース

## スキーマ

```ruby
# users table
# - id: bigint
# - email: string (unique index)
# - deleted_at: datetime (soft delete)
# - lock_version: integer (optimistic locking)

# products table
# - id: bigint
# - name: string
# - price: decimal(10,2)
```

## モデル・サービス

```ruby
class User < ApplicationRecord
  default_scope { where(deleted_at: nil) }

  def soft_delete!
    update!(deleted_at: Time.current)
  end
end

class Product < ApplicationRecord
  # 注文時点の商品情報はスナップショットとして保存すること
end
```
