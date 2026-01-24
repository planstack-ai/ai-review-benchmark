# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  name       :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#

# == Schema Information
#
# Table name: coupons
#
#  id          :bigint           not null, primary key
#  code        :string           not null
#  discount    :decimal(8,2)     not null
#  expires_at  :datetime
#  user_id     :bigint           not null
#  used_at     :datetime
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#

# == Schema Information
#
# Table name: orders
#
#  id         :bigint           not null, primary key
#  user_id    :bigint           not null
#  coupon_id  :bigint
#  total      :decimal(10,2)    not null
#  status     :string           default("pending")
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
```

## Models

```ruby
class User < ApplicationRecord
  has_many :coupons, dependent: :destroy
  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true

  def owns_coupon?(coupon)
    coupons.include?(coupon)
  end
end

class Coupon < ApplicationRecord
  belongs_to :user
  has_many :orders

  validates :code, presence: true, uniqueness: true
  validates :discount, presence: true, numericality: { greater_than: 0 }

  scope :active, -> { where(used_at: nil).where('expires_at IS NULL OR expires_at > ?', Time.current) }
  scope :expired, -> { where('expires_at IS NOT NULL AND expires_at <= ?', Time.current) }
  scope :used, -> { where.not(used_at: nil) }

  def expired?
    expires_at.present? && expires_at <= Time.current
  end

  def used?
    used_at.present?
  end

  def available?
    !expired? && !used?
  end

  def mark_as_used!
    update!(used_at: Time.current)
  end
end

class Order < ApplicationRecord
  belongs_to :user
  belongs_to :coupon, optional: true

  validates :total, presence: true, numericality: { greater_than: 0 }
  validates :status, inclusion: { in: %w[pending confirmed cancelled] }

  scope :with_coupons, -> { where.not(coupon_id: nil) }
  scope :confirmed, -> { where(status: 'confirmed') }

  def apply_coupon(coupon)
    return false unless coupon&.available?
    
    self.coupon = coupon
    self.total = calculate_discounted_total(coupon.discount)
    true
  end

  private

  def calculate_discounted_total(discount)
    [total - discount, 0].max
  end
end
```