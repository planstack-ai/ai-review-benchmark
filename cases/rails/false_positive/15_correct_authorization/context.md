# 既存コードベース情報

## Article モデル

```ruby
class Article < ApplicationRecord
  belongs_to :author, class_name: "User"
end
```

## User モデル

```ruby
class User < ApplicationRecord
  enum role: { user: 0, editor: 1, admin: 2 }

  def admin?
    role == "admin"
  end
end
```
