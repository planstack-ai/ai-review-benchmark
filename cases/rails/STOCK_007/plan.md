# Duplicate Stock Restoration

## 概要

ECサイトの注文処理における機能実装。

## 要件

1. Restore stock once per cancellation

## 使用すべき既存実装

- 既存のモデルメソッド・スコープを活用すること
- context.md に記載の実装を参照

## 注意事項

- 正しい実装パターン: `return if already_restored?; restore_stock`
- 仕様通りに実装すること
