# 既存コードベース情報

## TaxCalculator

```ruby
module TaxCalculator
  TAX_RATE = 0.10

  def self.with_tax(price, rate = TAX_RATE)
    (price * (1 + rate)).floor
  end
end
```

## Product モデル

```ruby
class Product < ApplicationRecord
  validates :price, presence: true, numericality: { greater_than: 0 }
end
```
