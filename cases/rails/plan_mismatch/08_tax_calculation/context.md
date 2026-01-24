# 既存コードベース情報

## TaxCalculator

```ruby
module TaxCalculator
  TAX_RATE = 0.1

  # 税抜価格から税込価格を計算
  def self.tax_included_price(price)
    (price * (1 + TAX_RATE)).floor
  end

  # 税抜価格から消費税額を計算
  def self.tax_amount(price)
    (price * TAX_RATE).floor
  end

  # 税込価格から税抜価格を逆算
  def self.tax_excluded_price(price_with_tax)
    (price_with_tax / (1 + TAX_RATE)).floor
  end
end
```

## Order / OrderItem モデル

```ruby
class Order < ApplicationRecord
  has_many :order_items

  def subtotal
    order_items.sum(&:line_total)
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  # 税抜の小計
  def line_total
    product.price * quantity  # product.priceは税抜
  end
end
```

## Product モデル

```ruby
class Product < ApplicationRecord
  # price: integer - 税抜価格（円）
end
```
