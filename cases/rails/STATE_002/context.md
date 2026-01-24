# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: orders
#
#  id           :bigint           not null, primary key
#  status       :string           not null
#  total_amount :decimal(10,2)    not null
#  created_at   :datetime         not null
#  updated_at   :datetime         not null
#  user_id      :bigint           not null
#
# Table name: shipments
#
#  id         :bigint           not null, primary key
#  status     :string           not null
#  shipped_at :datetime
#  created_at :datetime         not null
#  updated_at :datetime         not null
#  order_id   :bigint           not null
#
```

## Models

```ruby
class Order < ApplicationRecord
  belongs_to :user
  has_one :shipment, dependent: :destroy

  validates :status, presence: true, inclusion: { in: %w[pending confirmed processing cancelled] }
  validates :total_amount, presence: true, numericality: { greater_than: 0 }

  scope :active, -> { where.not(status: 'cancelled') }
  scope :pending, -> { where(status: 'pending') }
  scope :confirmed, -> { where(status: 'confirmed') }
  scope :processing, -> { where(status: 'processing') }
  scope :cancelled, -> { where(status: 'cancelled') }

  def pending?
    status == 'pending'
  end

  def confirmed?
    status == 'confirmed'
  end

  def processing?
    status == 'processing'
  end

  def cancelled?
    status == 'cancelled'
  end

  def confirm!
    update!(status: 'confirmed')
    create_shipment!(status: 'preparing')
  end

  def process!
    update!(status: 'processing')
  end

  private

  def create_shipment_record
    Shipment.create!(order: self, status: 'preparing')
  end
end

class Shipment < ApplicationRecord
  belongs_to :order

  validates :status, presence: true, inclusion: { in: %w[preparing shipped delivered] }

  scope :preparing, -> { where(status: 'preparing') }
  scope :shipped, -> { where(status: 'shipped') }
  scope :delivered, -> { where(status: 'delivered') }

  def preparing?
    status == 'preparing'
  end

  def shipped?
    status == 'shipped'
  end

  def delivered?
    status == 'delivered'
  end

  def ship!
    update!(status: 'shipped', shipped_at: Time.current)
  end

  def deliver!
    update!(status: 'delivered')
  end
end

class User < ApplicationRecord
  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: true
end
```