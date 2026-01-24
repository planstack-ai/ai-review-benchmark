# Existing Codebase

## Schema

```ruby
# db/schema.rb

# create_table "users", force: :cascade do |t|
#   t.string "email", null: false
#   t.string "first_name"
#   t.string "last_name"
#   t.boolean "active"
#   t.integer "role"
#   t.datetime "last_login_at"
#   t.timestamps null: false
# end

# create_table "posts", force: :cascade do |t|
#   t.string "title", null: false
#   t.text "content"
#   t.string "status"
#   t.boolean "featured"
#   t.integer "view_count"
#   t.decimal "rating", precision: 3, scale: 2
#   t.references "user", null: false, foreign_key: true
#   t.datetime "published_at"
#   t.timestamps null: false
# end

# create_table "comments", force: :cascade do |t|
#   t.text "body", null: false
#   t.boolean "approved"
#   t.integer "likes_count"
#   t.references "post", null: false, foreign_key: true
#   t.references "user", null: false, foreign_key: true
#   t.timestamps null: false
# end
```

## Models

```ruby
# app/models/user.rb
class User < ApplicationRecord
  ROLES = %w[admin moderator author reader].freeze
  
  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :destroy
  
  validates :email, presence: true, uniqueness: true
  validates :role, inclusion: { in: ROLES }
  
  enum role: ROLES.index_by(&:itself)
  
  scope :active, -> { where(active: true) }
  scope :inactive, -> { where(active: false) }
  scope :recently_logged_in, -> { where('last_login_at > ?', 30.days.ago) }
  
  def full_name
    "#{first_name} #{last_name}".strip
  end
  
  def display_name
    full_name.present? ? full_name : email
  end
end

# app/models/post.rb
class Post < ApplicationRecord
  STATUSES = %w[draft published archived].freeze
  
  belongs_to :user
  has_many :comments, dependent: :destroy
  
  validates :title, presence: true
  validates :status, inclusion: { in: STATUSES }
  validates :rating, numericality: { 
    greater_than_or_equal_to: 0, 
    less_than_or_equal_to: 5 
  }, allow_nil: true
  
  scope :published, -> { where(status: 'published') }
  scope :featured, -> { where(featured: true) }
  scope :by_popularity, -> { order(view_count: :desc) }
  scope :recent, -> { order(created_at: :desc) }
  
  def published?
    status == 'published' && published_at.present?
  end
  
  def increment_view_count!
    increment!(:view_count)
  end
end

# app/models/comment.rb
class Comment < ApplicationRecord
  belongs_to :post
  belongs_to :user
  
  validates :body, presence: true
  
  scope :approved, -> { where(approved: true) }
  scope :pending, -> { where(approved: false) }
  scope :popular, -> { where('likes_count > ?', 5) }
  
  def approve!
    update!(approved: true)
  end
  
  def increment_likes!
    increment!(:likes_count)
  end
end
```