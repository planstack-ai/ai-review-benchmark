# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  customer_id  :bigint           not null
#  total_amount :decimal(10, 2)   not null
#  status       :string           default("pending"), not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: items (order line items)
#
#  id           :bigint           not null, primary key
#  order_id     :bigint           not null
#  product_name :string           not null
#  quantity     :integer          not null
#  price        :decimal(10, 2)   not null
#  status       :string           default("pending"), not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Table name: customers
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  email      :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class Order < ApplicationRecord
  STATUSES = %w[pending confirmed shipped delivered cancelled].freeze

  belongs_to :customer
  has_many :items, dependent: :destroy

  validates :total_amount, presence: true, numericality: { greater_than_or_equal_to: 0 }
  validates :status, inclusion: { in: STATUSES }

  scope :pending, -> { where(status: 'pending') }
  scope :completed, -> { where(status: 'delivered') }
end

class Item < ApplicationRecord
  STATUSES = %w[pending packed shipped delivered].freeze

  belongs_to :order

  validates :product_name, presence: true
  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }
  validates :status, inclusion: { in: STATUSES }

  scope :shipped, -> { where(status: 'shipped') }
  scope :pending, -> { where(status: 'pending') }
end

class Customer < ApplicationRecord
  has_many :orders, dependent: :destroy

  validates :name, presence: true
  validates :email, presence: true, uniqueness: true
end
```

## Query Optimization Notes

When querying orders with associated items:
- Use `joins(:items)` with aggregation functions for database-level calculations
- Avoid `includes(:items).where(items: {...})` as it loads all data into memory
- Prefer `preload` over `includes` when you need eager loading without filtering on associations
- Use database GROUP BY and SUM for aggregation instead of Ruby enumeration
