# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  user_id      :bigint           not null
#  total_amount :decimal(10,2)    not null
#  status       :integer                    # NOTE: nullable, no default
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#
# Migration history:
#   2023-01-15: Initial orders table (no status column)
#   2024-06-01: Added status column (nullable integer, no default)
#               Note: ~50,000 existing orders have NULL status
#               These are legacy orders that should be treated as pending
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_many :order_items, dependent: :destroy

  # Status enum added in 2024 migration
  # NOTE: Legacy orders before this migration have NULL status
  enum status: {
    pending: 0,
    processing: 1,
    shipped: 2,
    delivered: 3,
    cancelled: 4,
    failed: 5
  }

  validates :total_amount, presence: true, numericality: { greater_than: 0 }

  scope :recent, -> { where('created_at > ?', 30.days.ago) }
  scope :in_date_range, ->(start_date, end_date) { where(created_at: start_date..end_date) }
end
```

## Usage Guidelines

- When querying by enum status, remember that enum scopes use exact equality matching
- Legacy data with NULL enum values will not be matched by enum scopes
- Consider NULL handling when querying enum columns that may contain legacy data
