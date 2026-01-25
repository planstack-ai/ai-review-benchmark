# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  role       :string           not null
#  active     :boolean          default(true)
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: organizations
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  active     :boolean          default(true)
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: user_organizations
#
#  id              :bigint           not null, primary key
#  user_id         :bigint           not null
#  organization_id :bigint           not null
#  role            :string           not null
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
#
# Table name: projects
#
#  id              :bigint           not null, primary key
#  name            :string           not null
#  organization_id :bigint           not null
#  status          :string           default("active")
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  ROLES = %w[admin manager member].freeze
  
  has_many :user_organizations, dependent: :destroy
  has_many :organizations, through: :user_organizations
  
  validates :email, presence: true, uniqueness: true
  validates :role, inclusion: { in: ROLES }
  
  scope :active, -> { where(active: true) }
  scope :by_role, ->(role) { where(role: role) }
  
  def admin?
    role == 'admin'
  end
  
  def manager?
    role == 'manager'
  end
  
  def member?
    role == 'member'
  end
  
  def organization_role(organization)
    user_organizations.find_by(organization: organization)&.role
  end
end

class Organization < ApplicationRecord
  has_many :user_organizations, dependent: :destroy
  has_many :users, through: :user_organizations
  has_many :projects, dependent: :destroy
  
  validates :name, presence: true
  
  scope :active, -> { where(active: true) }
end

class UserOrganization < ApplicationRecord
  ORG_ROLES = %w[owner admin member viewer].freeze
  
  belongs_to :user
  belongs_to :organization
  
  validates :role, inclusion: { in: ORG_ROLES }
  validates :user_id, uniqueness: { scope: :organization_id }
  
  scope :by_role, ->(role) { where(role: role) }
  scope :owners, -> { where(role: 'owner') }
  scope :admins, -> { where(role: 'admin') }
end

class Project < ApplicationRecord
  STATUSES = %w[active archived].freeze
  
  belongs_to :organization
  
  validates :name, presence: true
  validates :status, inclusion: { in: STATUSES }
  
  scope :active, -> { where(status: 'active') }
  scope :archived, -> { where(status: 'archived') }
  
  def active?
    status == 'active'
  end
end
```