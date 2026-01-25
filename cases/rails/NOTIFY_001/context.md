# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id                          :bigint           not null, primary key
#  user_id                     :bigint           not null
#  status                      :string           not null
#  total_amount                :decimal(10,2)    not null
#  confirmation_email_sent_at  :datetime
#  created_at                  :datetime         not null
#  updated_at                  :datetime         not null
#
# Table name: line_items (order line items)
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  price      :decimal(8,2)     not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  name       :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: products
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  price      :decimal(8,2)     not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true
end

class Order < ApplicationRecord
  belongs_to :user
  has_many :line_items, dependent: :destroy
  has_many :products, through: :line_items

  validates :status, presence: true, inclusion: { in: %w[pending confirmed shipped delivered cancelled] }
  validates :total_amount, presence: true, numericality: { greater_than: 0 }

  scope :confirmed, -> { where(status: 'confirmed') }
  scope :pending_confirmation, -> { where(status: 'confirmed', confirmation_email_sent_at: nil) }
  scope :confirmation_sent, -> { where.not(confirmation_email_sent_at: nil) }

  def confirmation_email_sent?
    confirmation_email_sent_at.present?
  end

  def order_number
    "ORD-#{id.to_s.rjust(6, '0')}"
  end
end

class LineItem < ApplicationRecord
  self.table_name = 'line_items'

  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }
end

class Product < ApplicationRecord
  has_many :line_items, dependent: :destroy
  has_many :orders, through: :line_items

  validates :name, presence: true
  validates :price, presence: true, numericality: { greater_than: 0 }
end
```

## Services

```ruby
class EmailService
  def send_order_confirmation(to:, order_id:, order_total:, items:)
    # External email delivery service
    # Raises EmailDeliveryError on failure
  end
end

class EmailDeliveryError < StandardError; end
```

## Email Delivery Guidelines

When implementing email sending with retry logic:
- Always check `email_already_sent?` before each send attempt (including retries)
- Retry logic should go through the same deduplication checks as the initial send
- Use idempotent operations to prevent duplicate sends in concurrent scenarios
- Mark email as sent only after successful delivery, before returning success
