# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  has_many :exchanges

  def deduct_points(amount)
    raise InsufficientPointsError if points < amount
    decrement!(:points, amount)
  end
end
```

## Exchange モデル

```ruby
class Exchange < ApplicationRecord
  belongs_to :user
  belongs_to :product

  validates :points_used, presence: true
end
```
