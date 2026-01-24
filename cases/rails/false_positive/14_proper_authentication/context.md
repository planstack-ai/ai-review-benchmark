# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  has_secure_password

  validates :email, presence: true, uniqueness: { case_sensitive: false }
end
```

## has_secure_password

```ruby
# has_secure_password が提供するメソッド
# authenticate(password) - パスワードが正しければ self、間違いなら false を返す
```
