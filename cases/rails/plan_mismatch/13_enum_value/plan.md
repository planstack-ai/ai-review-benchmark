# 注文ステータス更新サービス

## 概要
注文のステータスを次のステップに進める。

## 要件

1. 注文ステータスを次のステップに更新する
2. ステータス遷移: pending → **paid** → shipped → delivered
3. 不正な遷移の場合はエラーを発生させる

## 使用すべき既存実装

- `Order#status` - 現在のステータス（enum）
- `Order#paid!`, `Order#shipped!`, `Order#delivered!` - ステータス更新メソッド
- `Order::VALID_TRANSITIONS` - 有効な遷移の定義

## 注意事項

- pending の次は **paid**（confirmed ではない）
- 定義済みの遷移ルールに従うこと
