# Find Or Create Race

## 概要

ECサイトの注文処理における機能実装。

## 要件

1. Handle concurrent find_or_create

## 使用すべき既存実装

- 既存のモデルメソッド・スコープを活用すること
- context.md に記載の実装を参照

## 注意事項

- 正しい実装パターン: `find_or_create_by with unique constraint + rescue`
- 仕様通りに実装すること
