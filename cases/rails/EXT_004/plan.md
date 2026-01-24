# Retry Duplicate Order

## 概要

ECサイトの注文処理における機能実装。

## 要件

1. Prevent duplicate orders on retry

## 使用すべき既存実装

- 既存のモデルメソッド・スコープを活用すること
- context.md に記載の実装を参照

## 注意事項

- 正しい実装パターン: `Order.find_or_create_by(idempotency_key: key)`
- 仕様通りに実装すること
