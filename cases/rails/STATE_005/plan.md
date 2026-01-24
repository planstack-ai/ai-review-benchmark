# Partial Cancel Integrity

## 概要

ECサイトの注文処理における機能実装。

## 要件

1. Update total correctly on partial cancellation

## 使用すべき既存実装

- 既存のモデルメソッド・スコープを活用すること
- context.md に記載の実装を参照

## 注意事項

- 正しい実装パターン: `recalculate_total after partial_cancel`
- 仕様通りに実装すること
