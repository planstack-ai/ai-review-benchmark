# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id                     :bigint           not null, primary key
#  email                  :string           default(""), not null
#  encrypted_password     :string           default(""), not null
#  first_name             :string
#  last_name              :string
#  member_since           :datetime
#  membership_status      :string           default("guest")
#  created_at             :datetime         not null
#  updated_at             :datetime         not null
#
# Table name: products
#
#  id                     :bigint           not null, primary key
#  name                   :string           not null
#  description            :text
#  base_price_cents       :integer          not null
#  member_price_cents     :integer
#  category               :string
#  active                 :boolean          default(true)
#  created_at             :datetime         not null
#  updated_at             :datetime         not null
#
# Table name: line_items
#
#  id                     :bigint           not null, primary key
#  cart_id                :bigint           not null
#  product_id             :bigint           not null
#  quantity               :integer          default(1)
#  unit_price_cents       :integer          not null
#  created_at             :datetime         not null
#  updated_at             :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  devise :database_authenticatable, :registerable

  MEMBERSHIP_STATUSES = %w[guest active premium suspended].freeze

  validates :membership_status, inclusion: { in: MEMBERSHIP_STATUSES }

  scope :members, -> { where.not(membership_status: 'guest') }
  scope :active_members, -> { where(membership_status: %w[active premium]) }

  def member?
    membership_status != 'guest'
  end

  def active_member?
    %w[active premium].include?(membership_status)
  end

  def guest?
    membership_status == 'guest'
  end
end

class Product < ApplicationRecord
  validates :name, presence: true
  validates :base_price_cents, presence: true, numericality: { greater_than: 0 }
  validates :member_price_cents, numericality: { greater_than: 0, allow_nil: true }

  scope :active, -> { where(active: true) }
  scope :with_member_pricing, -> { where.not(member_price_cents: nil) }

  monetize :base_price_cents
  monetize :member_price_cents, allow_nil: true

  def has_member_pricing?
    member_price_cents.present?
  end

  def price_for_user(user)
    if user&.active_member? && has_member_pricing?
      member_price
    else
      base_price
    end
  end
end

class Cart < ApplicationRecord
  belongs_to :user, optional: true
  has_many :line_items, dependent: :destroy
  has_many :products, through: :line_items

  def guest_cart?
    user_id.nil?
  end

  def member_cart?
    user&.member?
  end

  def total_cents
    line_items.sum(:unit_price_cents)
  end
end

class LineItem < ApplicationRecord
  belongs_to :cart
  belongs_to :product

  validates :quantity, presence: true, numericality: { greater_than: 0 }
  validates :unit_price_cents, presence: true, numericality: { greater_than: 0 }

  monetize :unit_price_cents

  def total_cents
    unit_price_cents * quantity
  end
end
```