# Transaction Nesting

## 概要

ECサイトの注文処理における機能実装。

## 要件

1. Handle nested transactions correctly

## 使用すべき既存実装

- 既存のモデルメソッド・スコープを活用すること
- context.md に記載の実装を参照

## 注意事項

- 正しい実装パターン: `transaction(requires_new: true) { ... }`
- 仕様通りに実装すること
