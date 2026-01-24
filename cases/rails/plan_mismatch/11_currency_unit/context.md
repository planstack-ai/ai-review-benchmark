# 既存コードベース情報

## MoneyConverter

```ruby
module MoneyConverter
  # 円から銭に変換
  def self.yen_to_sen(yen)
    yen * 100
  end

  # 銭から円に変換
  def self.sen_to_yen(sen)
    sen / 100
  end
end
```

## PaymentGateway

```ruby
module PaymentGateway
  # 決済を実行
  # @param amount [Integer] 金額（銭単位）
  # @return [String] トランザクションID
  def self.charge(amount_in_sen)
    response = ExternalPaymentAPI.post('/charge', amount: amount_in_sen)
    response['transaction_id']
  end
end
```

## Order モデル

```ruby
class Order < ApplicationRecord
  # total: integer - 合計金額（円単位）
  # transaction_id: string - 決済トランザクションID

  def record_payment(transaction_id)
    update!(transaction_id: transaction_id, paid_at: Time.current)
  end
end
```
