# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  enum role: { user: 0, moderator: 1, admin: 2 }

  validates :name, presence: true
  validates :email, presence: true
end
```
