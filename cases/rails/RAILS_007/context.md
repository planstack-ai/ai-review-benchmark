# Existing Codebase

## Schema

```ruby
# db/schema.rb
# create_table "users", force: :cascade do |t|
#   t.string "email", null: false
#   t.string "name", null: false
#   t.datetime "created_at", null: false
#   t.datetime "updated_at", null: false
#   t.index ["email"], name: "index_users_on_email", unique: true
# end

# create_table "categories", force: :cascade do |t|
#   t.string "name", null: false
#   t.string "slug", null: false
#   t.text "description"
#   t.datetime "created_at", null: false
#   t.datetime "updated_at", null: false
#   t.index ["name"], name: "index_categories_on_name", unique: true
#   t.index ["slug"], name: "index_categories_on_slug", unique: true
# end

# create_table "tags", force: :cascade do |t|
#   t.string "name", null: false
#   t.string "color", default: "#3498db"
#   t.integer "usage_count", default: 0
#   t.datetime "created_at", null: false
#   t.datetime "updated_at", null: false
#   t.index ["name"], name: "index_tags_on_name", unique: true
# end
```

## Models

```ruby
class User < ApplicationRecord
  validates :email, presence: true, uniqueness: true
  validates :name, presence: true

  scope :by_email, ->(email) { where(email: email) }
  
  def self.find_by_email_case_insensitive(email)
    where("LOWER(email) = ?", email.downcase).first
  end
end

class Category < ApplicationRecord
  validates :name, presence: true, uniqueness: true
  validates :slug, presence: true, uniqueness: true

  before_validation :generate_slug, if: -> { name.present? && slug.blank? }

  scope :by_name, ->(name) { where(name: name) }
  scope :by_slug, ->(slug) { where(slug: slug) }

  private

  def generate_slug
    self.slug = name.parameterize
  end
end

class Tag < ApplicationRecord
  validates :name, presence: true, uniqueness: true
  validates :color, presence: true

  scope :by_name, ->(name) { where(name: name) }
  scope :popular, -> { where("usage_count > ?", 10) }

  def increment_usage!
    increment!(:usage_count)
  end

  def self.normalize_name(name)
    name.strip.downcase
  end
end

class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class

  def self.find_or_create_by_with_retry(attributes, &block)
    retries = 0
    begin
      find_or_create_by(attributes, &block)
    rescue ActiveRecord::RecordNotUnique
      retries += 1
      retry if retries <= 3
      raise
    end
  end

  def self.with_advisory_lock(key, &block)
    connection.with_advisory_lock(key, &block)
  end
end
```

## Usage Guidelines

- Use database constraints (unique indexes) in addition to ActiveRecord validations to prevent race conditions when creating records.

