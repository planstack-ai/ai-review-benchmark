# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: coupons
#
#  id          :bigint           not null, primary key
#  code        :string           not null
#  discount    :decimal(8,2)     not null
#  expires_at  :date
#  active      :boolean          default(true), not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_coupons_on_code        (code) UNIQUE
#  index_coupons_on_expires_at  (expires_at)
#

# Table name: orders
#
#  id         :bigint           not null, primary key
#  user_id    :bigint           not null
#  coupon_id  :bigint
#  total      :decimal(10,2)    not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_orders_on_coupon_id  (coupon_id)
#  index_orders_on_user_id    (user_id)
#
```

## Models

```ruby
class Coupon < ApplicationRecord
  has_many :orders, dependent: :nullify
  
  validates :code, presence: true, uniqueness: true
  validates :discount, presence: true, numericality: { greater_than: 0 }
  
  scope :active, -> { where(active: true) }
  scope :with_expiry, -> { where.not(expires_at: nil) }
  scope :without_expiry, -> { where(expires_at: nil) }
  
  def self.find_by_code(code)
    find_by(code: code&.upcase)
  end
  
  def expired?
    expires_at.present? && expires_at < Date.current
  end
  
  def never_expires?
    expires_at.nil?
  end
  
  def days_until_expiry
    return nil if never_expires?
    (expires_at - Date.current).to_i
  end
  
  def percentage_discount?
    discount <= 1.0
  end
  
  def fixed_amount_discount?
    discount > 1.0
  end
  
  private
  
  def normalize_code
    self.code = code&.upcase&.strip
  end
end

class Order < ApplicationRecord
  belongs_to :user
  belongs_to :coupon, optional: true
  
  validates :total, presence: true, numericality: { greater_than: 0 }
  
  scope :with_coupons, -> { joins(:coupon) }
  scope :recent, -> { order(created_at: :desc) }
  
  def discounted_total
    return total unless coupon
    
    if coupon.percentage_discount?
      total * (1 - coupon.discount)
    else
      [total - coupon.discount, 0].max
    end
  end
  
  def discount_amount
    total - discounted_total
  end
end

class User < ApplicationRecord
  has_many :orders, dependent: :destroy
  
  validates :email, presence: true, uniqueness: true
  
  def recent_orders
    orders.recent.limit(10)
  end
end
```