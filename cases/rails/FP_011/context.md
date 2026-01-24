# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id                     :bigint           not null, primary key
#  email                  :string           not null
#  first_name             :string
#  last_name              :string
#  role                   :string           default("user"), not null
#  status                 :string           default("active"), not null
#  admin_bypass_enabled   :boolean          default(false), not null
#  created_at             :datetime         not null
#  updated_at             :datetime         not null
#
# Indexes
#
#  index_users_on_email  (email) UNIQUE
#  index_users_on_role   (role)
#

# Table name: test_accounts
#
#  id          :bigint           not null, primary key
#  user_id     :bigint           not null
#  account_type :string          not null
#  test_data   :json
#  expires_at  :datetime
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Indexes
#
#  index_test_accounts_on_user_id  (user_id)
#
# Foreign Keys
#
#  fk_rails_...  (user_id => users.id)
#
```

## Models

```ruby
class User < ApplicationRecord
  ROLES = %w[user admin super_admin].freeze
  STATUSES = %w[active inactive suspended].freeze

  validates :email, presence: true, uniqueness: true
  validates :role, inclusion: { in: ROLES }
  validates :status, inclusion: { in: STATUSES }

  scope :admins, -> { where(role: %w[admin super_admin]) }
  scope :active, -> { where(status: 'active') }
  scope :with_bypass, -> { where(admin_bypass_enabled: true) }

  has_many :test_accounts, dependent: :destroy

  def admin?
    %w[admin super_admin].include?(role)
  end

  def super_admin?
    role == 'super_admin'
  end

  def bypass_enabled?
    admin_bypass_enabled && admin?
  end

  def full_name
    "#{first_name} #{last_name}".strip
  end
end

class TestAccount < ApplicationRecord
  ACCOUNT_TYPES = %w[demo sandbox staging].freeze

  belongs_to :user

  validates :account_type, inclusion: { in: ACCOUNT_TYPES }
  validates :user_id, presence: true
  validates :expires_at, presence: true

  scope :active, -> { where('expires_at > ?', Time.current) }
  scope :expired, -> { where('expires_at <= ?', Time.current) }
  scope :by_type, ->(type) { where(account_type: type) }

  def expired?
    expires_at <= Time.current
  end

  def days_until_expiry
    return 0 if expired?
    ((expires_at - Time.current) / 1.day).ceil
  end
end

class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class

  def self.skip_validation_for_bypass_users
    validate :check_bypass_permissions, unless: :bypass_validations?

    private

    def bypass_validations?
      return false unless respond_to?(:user)
      user&.bypass_enabled?
    end

    def check_bypass_permissions
      # Override in subclasses
    end
  end
end
```