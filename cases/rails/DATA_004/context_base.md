# Existing Codebase

## Schema

```ruby
# db/migrate/20231201000001_create_users.rb
# create_table :users do |t|
#   t.string :name, null: false
#   t.string :email, null: false
#   t.datetime :deleted_at
#   t.timestamps
# end
# add_index :users, :deleted_at

# db/migrate/20231201000002_create_posts.rb
# create_table :posts do |t|
#   t.string :title, null: false
#   t.text :content
#   t.references :user, null: false, foreign_key: true
#   t.datetime :deleted_at
#   t.boolean :published, default: false
#   t.timestamps
# end
# add_index :posts, :deleted_at

# db/migrate/20231201000003_create_comments.rb
# create_table :comments do |t|
#   t.text :body, null: false
#   t.references :post, null: false, foreign_key: true
#   t.references :user, null: false, foreign_key: true
#   t.datetime :deleted_at
#   t.timestamps
# end
# add_index :comments, :deleted_at
```

## Models

```ruby
# app/models/application_record.rb
class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class

  scope :active, -> { where(deleted_at: nil) }
  scope :deleted, -> { where.not(deleted_at: nil) }

  def soft_delete!
    update!(deleted_at: Time.current)
  end

  def restore!
    update!(deleted_at: nil)
  end

  def deleted?
    deleted_at.present?
  end
end

# app/models/user.rb
class User < ApplicationRecord
  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :destroy

  validates :name, presence: true
  validates :email, presence: true, uniqueness: true

  scope :by_email, ->(email) { where(email: email) }
end

# app/models/post.rb
class Post < ApplicationRecord
  belongs_to :user
  has_many :comments, dependent: :destroy

  validates :title, presence: true

  scope :published, -> { where(published: true) }
  scope :by_user, ->(user) { where(user: user) }
  scope :recent, -> { order(created_at: :desc) }
end

# app/models/comment.rb
class Comment < ApplicationRecord
  belongs_to :post
  belongs_to :user

  validates :body, presence: true

  scope :by_post, ->(post) { where(post: post) }
  scope :by_user, ->(user) { where(user: user) }
  scope :recent, -> { order(created_at: :desc) }
end

# app/controllers/application_controller.rb
class ApplicationController < ActionController::Base
  private

  def current_user
    @current_user ||= User.find(session[:user_id]) if session[:user_id]
  end
end

# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  def index
    @posts = Post.published.includes(:user)
  end

  def show
    @post = Post.find(params[:id])
    @comments = @post.comments.includes(:user)
  end
end
```
