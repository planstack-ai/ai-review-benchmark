# 既存コードベース

## スキーマ

```ruby
# users table
# - id: bigint
# - email: string
# - role: integer (enum: user, admin)
# - membership_status: string (active, inactive)

# orders table
# - id: bigint
# - user_id: bigint (foreign key)
```

## モデル・サービス

```ruby
class User < ApplicationRecord
  has_many :orders

  enum role: { user: 0, admin: 1 }

  def admin?
    role == 'admin'
  end

  def member?
    membership_status == 'active'
  end
end

class ApplicationController < ActionController::Base
  def current_user
    @current_user ||= User.find(session[:user_id])
  end
end
```
