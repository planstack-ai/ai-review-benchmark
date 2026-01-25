# Existing Codebase

## Schema

```ruby
# db/schema.rb
# create_table "users", force: :cascade do |t|
#   t.string "email", null: false
#   t.string "first_name"
#   t.string "last_name"
#   t.string "encrypted_password", null: false
#   t.datetime "created_at", null: false
#   t.datetime "updated_at", null: false
# end

# create_table "user_profiles", force: :cascade do |t|
#   t.bigint "user_id", null: false
#   t.string "bio"
#   t.string "avatar_url"
#   t.datetime "created_at", null: false
#   t.datetime "updated_at", null: false
#   t.index ["user_id"], name: "index_user_profiles_on_user_id", unique: true
# end

# create_table "organizations", force: :cascade do |t|
#   t.string "name", null: false
#   t.string "slug", null: false
#   t.string "contact_email"
#   t.datetime "created_at", null: false
#   t.datetime "updated_at", null: false
#   t.index ["slug"], name: "index_organizations_on_slug", unique: true
# end
```

## Models

```ruby
# app/models/application_record.rb
class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class
end

# app/models/user.rb
class User < ApplicationRecord
  has_secure_password
  
  has_one :user_profile, dependent: :destroy
  has_many :memberships, dependent: :destroy
  has_many :organizations, through: :memberships
  
  validates :email, presence: true, format: { with: URI::MailTo::EMAIL_REGEXP }
  validates :first_name, :last_name, presence: true
  
  before_save :normalize_email
  
  scope :active, -> { where(deleted_at: nil) }
  scope :by_email, ->(email) { where(email: email.downcase.strip) }
  
  def full_name
    "#{first_name} #{last_name}"
  end
  
  def display_email
    email.downcase
  end
  
  private
  
  def normalize_email
    self.email = email.downcase.strip if email.present?
  end
end

# app/models/user_profile.rb
class UserProfile < ApplicationRecord
  belongs_to :user
  
  validates :user_id, uniqueness: true
end

# app/models/organization.rb
class Organization < ApplicationRecord
  has_many :memberships, dependent: :destroy
  has_many :users, through: :memberships
  
  validates :name, presence: true
  validates :slug, presence: true, uniqueness: { case_sensitive: false }
  validates :contact_email, format: { with: URI::MailTo::EMAIL_REGEXP }, allow_blank: true
  
  before_validation :generate_slug, if: -> { slug.blank? && name.present? }
  
  scope :by_slug, ->(slug) { where(slug: slug.downcase) }
  
  private
  
  def generate_slug
    self.slug = name.parameterize
  end
end

# app/models/membership.rb
class Membership < ApplicationRecord
  belongs_to :user
  belongs_to :organization
  
  validates :user_id, uniqueness: { scope: :organization_id }
  
  enum role: { member: 0, admin: 1, owner: 2 }
end
```
