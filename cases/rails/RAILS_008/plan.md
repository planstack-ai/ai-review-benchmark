# Update All Skips Callbacks

## 概要

ECサイトの注文処理における機能実装。

## 要件

1. Use update when callbacks needed

## 使用すべき既存実装

- 既存のモデルメソッド・スコープを活用すること
- context.md に記載の実装を参照

## 注意事項

- 正しい実装パターン: `orders.find_each { |o| o.update(status: 'archived') }`
- 仕様通りに実装すること
