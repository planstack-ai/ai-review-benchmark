# Existing Codebase

## Schema

```ruby
# db/schema.rb
# create_table "articles", force: :cascade do |t|
#   t.string "title", null: false
#   t.text "content"
#   t.string "status", default: "draft"
#   t.bigint "user_id", null: false
#   t.integer "lock_version", default: 0, null: false
#   t.datetime "created_at", null: false
#   t.datetime "updated_at", null: false
#   t.index ["user_id"], name: "index_articles_on_user_id"
# end

# create_table "users", force: :cascade do |t|
#   t.string "email", null: false
#   t.string "name", null: false
#   t.datetime "created_at", null: false
#   t.datetime "updated_at", null: false
#   t.index ["email"], name: "index_users_on_email", unique: true
# end

# create_table "comments", force: :cascade do |t|
#   t.text "body", null: false
#   t.bigint "article_id", null: false
#   t.bigint "user_id", null: false
#   t.integer "lock_version", default: 0, null: false
#   t.datetime "created_at", null: false
#   t.datetime "updated_at", null: false
#   t.index ["article_id"], name: "index_comments_on_article_id"
#   t.index ["user_id"], name: "index_comments_on_user_id"
# end
```

## Models

```ruby
class User < ApplicationRecord
  has_many :articles, dependent: :destroy
  has_many :comments, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true

  scope :active, -> { where(active: true) }
end

class Article < ApplicationRecord
  belongs_to :user
  has_many :comments, dependent: :destroy

  validates :title, presence: true
  validates :content, presence: true
  validates :status, inclusion: { in: %w[draft published archived] }

  scope :published, -> { where(status: 'published') }
  scope :by_author, ->(user) { where(user: user) }
  scope :recent, -> { order(created_at: :desc) }

  def published?
    status == 'published'
  end

  def can_be_edited_by?(user)
    self.user == user || user.admin?
  end

  def word_count
    content.to_s.split.size
  end
end

class Comment < ApplicationRecord
  belongs_to :article
  belongs_to :user

  validates :body, presence: true, length: { minimum: 10 }

  scope :recent, -> { order(created_at: :desc) }
  scope :for_article, ->(article) { where(article: article) }

  def can_be_edited_by?(user)
    self.user == user || user.admin?
  end

  def excerpt(limit = 100)
    body.truncate(limit)
  end
end

class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class

  def self.find_for_edit(id)
    find(id)
  end

  private

  def handle_stale_object_error
    errors.add(:base, "This record has been modified by another user. Please reload and try again.")
    false
  end
end
```