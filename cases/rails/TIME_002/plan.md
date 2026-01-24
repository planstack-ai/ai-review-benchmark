# Sale Period Boundary

## 概要

ECサイトの注文処理における機能実装。

## 要件

1. Sale starts at midnight on start date

## 使用すべき既存実装

- 既存のモデルメソッド・スコープを活用すること
- context.md に記載の実装を参照

## 注意事項

- 正しい実装パターン: `start_date.beginning_of_day`
- 仕様通りに実装すること
