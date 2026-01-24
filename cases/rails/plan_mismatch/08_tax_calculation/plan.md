# 請求書生成

## 要件

1. 注文から請求書を生成する
2. 商品の価格は **税抜価格** で保存されている
3. 請求書には税込価格を表示する
4. 消費税率は10%

## 使用すべき既存実装

- `TaxCalculator.tax_included_price(price)` - 税抜価格から税込価格を計算
- `TaxCalculator.tax_amount(price)` - 税抜価格から消費税額を計算
- `TaxCalculator::TAX_RATE` - 消費税率（0.1）

## 注意事項

- 商品テーブルのpriceは税抜価格
- 計算は円未満切り捨て
- 税込価格 = 税抜価格 × 1.1（小数点以下切り捨て）
