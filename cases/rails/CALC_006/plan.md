# Free Shipping Boundary

## 概要

ECサイトの注文処理における機能実装。

## 要件

1. Free shipping for orders of 5000 yen or more

## 使用すべき既存実装

- 既存のモデルメソッド・スコープを活用すること
- context.md に記載の実装を参照

## 注意事項

- 正しい実装パターン: `total >= 5000 ? 0 : shipping_fee`
- 仕様通りに実装すること
