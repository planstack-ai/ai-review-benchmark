# 外部決済API連携

## 要件

1. 注文金額を外部決済APIに送信する
2. **外部APIは金額を「銭」単位（円の1/100）で受け取る**
3. 内部では「円」単位で管理している
4. 決済成功後、トランザクションIDを保存する

## 使用すべき既存実装

- `PaymentGateway.charge(amount_in_sen)` - 決済実行（銭単位）
- `MoneyConverter.yen_to_sen(yen)` - 円から銭に変換
- `MoneyConverter.sen_to_yen(sen)` - 銭から円に変換

## 注意事項

- 内部金額は「円」、外部APIは「銭」（100倍する必要あり）
- 例: 1000円 → 100000銭
- 変換には既存の `MoneyConverter` を使用すること
