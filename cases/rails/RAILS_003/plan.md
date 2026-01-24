# Callback Order Dependency

## 概要

ECサイトの注文処理における機能実装。

## 要件

1. Ensure callback execution order

## 使用すべき既存実装

- 既存のモデルメソッド・スコープを活用すること
- context.md に記載の実装を参照

## 注意事項

- 正しい実装パターン: `prepend: true for critical callbacks`
- 仕様通りに実装すること
