# 既存コードベース情報

## User モデル

```ruby
class User < ApplicationRecord
  enum role: { guest: 0, member: 1, admin: 2 }

  # 有料会員かどうかを返す
  def member?
    role == 'member' || role == 'admin'
  end

  # フルネームを返す
  def full_name
    "#{last_name} #{first_name}"
  end
end
```

## Order モデル

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items

  enum status: { pending: 0, confirmed: 1, shipped: 2, cancelled: 3 }

  # 割引率を適用する
  # @param rate [Float] 支払い割合（0.9 = 10%割引）
  def apply_discount(rate)
    self.total = (total * rate).floor
  end

  # 合計金額を計算
  def calculate_total
    self.total = order_items.sum { |item| item.price * item.quantity }
  end
end
```

## PaymentGateway

```ruby
module PaymentGateway
  # 決済を実行
  # @param amount [Integer] 決済金額
  # @return [Boolean] 成功/失敗
  def self.charge(amount)
    # 外部決済APIを呼び出し
    ExternalPaymentAPI.process(amount: amount)
  end
end
```
