# Manipulate Other Cart

## 概要

ECサイトの注文処理における機能実装。

## 要件

1. Users can only modify their own cart

## 使用すべき既存実装

- 既存のモデルメソッド・スコープを活用すること
- context.md に記載の実装を参照

## 注意事項

- 正しい実装パターン: `current_user.cart.add_item(item)`
- 仕様通りに実装すること
