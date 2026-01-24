# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  first_name :string           not null
#  last_name  :string           not null
#  phone      :string
#  status     :integer          default("active"), not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_users_on_email  (email) UNIQUE
#

# Table name: orders
#
#  id          :bigint           not null, primary key
#  user_id     :bigint           not null
#  total_cents :integer          not null
#  status      :integer          default("pending"), not null
#  notes       :text
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_orders_on_user_id  (user_id)
#
# Foreign Keys
#
#  fk_rails_...  (user_id => users.id)
#
```

## Models

```ruby
class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class
end

class User < ApplicationRecord
  EMAIL_REGEX = /\A[\w+\-.]+@[a-z\d\-]+(\.[a-z\d\-]+)*\.[a-z]+\z/i
  PHONE_REGEX = /\A\+?[\d\s\-\(\)]{10,15}\z/

  enum status: { active: 0, inactive: 1, suspended: 2 }

  has_many :orders, dependent: :destroy

  validates :email, presence: true, uniqueness: { case_sensitive: false }
  validates :email, format: { with: EMAIL_REGEX }
  validates :first_name, presence: true, length: { minimum: 2, maximum: 50 }
  validates :last_name, presence: true, length: { minimum: 2, maximum: 100 }
  validates :phone, format: { with: PHONE_REGEX }, allow_blank: true

  scope :active, -> { where(status: :active) }
  scope :by_email, ->(email) { where(email: email.downcase) }

  before_save :normalize_email

  def full_name
    "#{first_name} #{last_name}"
  end

  private

  def normalize_email
    self.email = email.downcase.strip if email.present?
  end
end

class Order < ApplicationRecord
  MINIMUM_TOTAL_CENTS = 100
  MAXIMUM_TOTAL_CENTS = 1_000_000_00

  enum status: { pending: 0, confirmed: 1, shipped: 2, delivered: 3, cancelled: 4 }

  belongs_to :user

  scope :recent, -> { where(created_at: 1.month.ago..) }
  scope :by_status, ->(status) { where(status: status) }
  scope :high_value, -> { where('total_cents >= ?', 10_000_00) }

  def total_dollars
    total_cents / 100.0
  end

  def can_be_cancelled?
    pending? || confirmed?
  end
end
```