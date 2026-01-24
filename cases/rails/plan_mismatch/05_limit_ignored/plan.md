# カートへの商品追加

## 要件

1. カートに商品を追加する
2. 同一商品の場合は数量を加算する
3. **1商品あたりの数量上限は100個**
4. 上限を超える場合はエラーを返す

## 使用すべき既存実装

- `CartItem.find_or_initialize_by(cart:, product:)` - カートアイテムの取得または初期化
- `CartItem::MAX_QUANTITY` - 数量上限定数（100）
- `CartItem#quantity_exceeded?` - 数量が上限を超えているか判定

## 注意事項

- 上限チェックは加算後の数量で行う
- 上限を超える場合はCartQuantityExceededErrorを発生させる
