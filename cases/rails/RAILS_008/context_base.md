# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id                     :bigint           not null, primary key
#  email                  :string           not null
#  name                   :string           not null
#  archived_orders_count  :integer          default(0)
#  last_archival_at       :datetime
#  notification_preferences :jsonb          default({})
#  created_at             :datetime         not null
#  updated_at             :datetime         not null
#
# Table name: orders
#
#  id              :bigint           not null, primary key
#  user_id         :bigint           not null
#  status          :string           default("pending"), not null
#  total_amount    :decimal(10, 2)   not null
#  archived_at     :datetime
#  archive_reason  :string
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
#
# Table name: order_items
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  product_id :bigint           not null
#  quantity   :integer          not null
#  price      :decimal(10, 2)   not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: payments
#
#  id         :bigint           not null, primary key
#  order_id   :bigint           not null
#  amount     :decimal(10, 2)   not null
#  status     :string           default("pending")
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true

  def notification_preferences
    super || {}
  end
end

class Order < ApplicationRecord
  STATUSES = %w[pending processing completed cancelled archived].freeze
  ARCHIVE_REASONS = %w[expired cancelled inactive].freeze

  belongs_to :user
  has_many :order_items, dependent: :destroy
  has_many :payments, dependent: :destroy

  validates :status, inclusion: { in: STATUSES }
  validates :archive_reason, inclusion: { in: ARCHIVE_REASONS }, allow_nil: true
  validates :total_amount, presence: true, numericality: { greater_than: 0 }

  # Important callbacks for order updates
  after_update :log_status_change, if: :saved_change_to_status?
  after_update :update_inventory, if: :saved_change_to_status?
  after_update :notify_user, if: :saved_change_to_status?
  after_update :record_audit_trail

  scope :pending, -> { where(status: 'pending') }
  scope :processing, -> { where(status: 'processing') }
  scope :archived, -> { where(status: 'archived') }

  private

  def log_status_change
    Rails.logger.info "Order #{id} status changed from #{status_before_last_save} to #{status}"
    AuditLog.create!(
      auditable: self,
      action: 'status_change',
      old_value: status_before_last_save,
      new_value: status
    )
  end

  def update_inventory
    return unless status == 'archived' || status == 'cancelled'
    order_items.each { |item| InventoryService.restore(item) }
  end

  def notify_user
    OrderMailer.status_update(self).deliver_later
  end

  def record_audit_trail
    OrderAuditService.record(self)
  end
end

class OrderItem < ApplicationRecord
  belongs_to :order
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :price, presence: true, numericality: { greater_than: 0 }
end

class Payment < ApplicationRecord
  belongs_to :order

  validates :amount, presence: true, numericality: { greater_than: 0 }
  validates :status, inclusion: { in: %w[pending completed failed refunded] }
end
```

## Mailers

```ruby
class UserMailer < ApplicationMailer
  def orders_archived(user:, archived_count:, archive_reason:)
    @user = user
    @archived_count = archived_count
    @archive_reason = archive_reason
    mail(to: user.email, subject: "#{archived_count} orders have been archived")
  end
end
```
