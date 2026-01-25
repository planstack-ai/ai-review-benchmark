# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: accounts
#
#  id         :bigint           not null, primary key
#  user_id    :bigint           not null
#  balance    :decimal(15,2)    default(0.0), not null
#  currency   :string           default("USD"), not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes:
#   index_accounts_on_user_id (user_id)
```

## Models

```ruby
class Account < ApplicationRecord
  belongs_to :user
  has_many :transfers_sent, class_name: 'Transfer', foreign_key: :from_account_id
  has_many :transfers_received, class_name: 'Transfer', foreign_key: :to_account_id

  validates :balance, presence: true, numericality: { greater_than_or_equal_to: 0 }
  validates :currency, presence: true

  def deposit!(amount)
    raise ArgumentError, "Amount must be positive" if amount <= 0
    increment!(:balance, amount)
  end

  def withdraw!(amount)
    raise ArgumentError, "Amount must be positive" if amount <= 0
    raise InsufficientFunds if balance < amount
    decrement!(:balance, amount)
  end
end

class Transfer < ApplicationRecord
  belongs_to :from_account, class_name: 'Account'
  belongs_to :to_account, class_name: 'Account'

  validates :amount, presence: true, numericality: { greater_than: 0 }
end

class InsufficientFunds < StandardError; end
```

## Usage Guidelines

- Use database transactions to ensure atomic updates across multiple records
- For operations that read-then-write based on current values, consider using pessimistic locking to prevent race conditions
