# Non Atomic Stock Update

## 概要

ECサイトの注文処理における機能実装。

## 要件

1. Atomically check and decrement stock

## 使用すべき既存実装

- 既存のモデルメソッド・スコープを活用すること
- context.md に記載の実装を参照

## 注意事項

- 正しい実装パターン: `Product.where('stock > 0').update_all('stock = stock - 1')`
- 仕様通りに実装すること
