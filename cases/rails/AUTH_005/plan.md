# Guest Member Pricing

## 概要

ECサイトの注文処理における機能実装。

## 要件

1. Member pricing only for logged-in members

## 使用すべき既存実装

- 既存のモデルメソッド・スコープを活用すること
- context.md に記載の実装を参照

## 注意事項

- 正しい実装パターン: `current_user&.member? ? member_price : regular_price`
- 仕様通りに実装すること
