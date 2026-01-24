# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id         :bigint           not null, primary key
#  email      :string           not null
#  name       :string           not null
#  status     :integer          default("active"), not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#  deleted_at :datetime
#
# Table name: posts
#
#  id          :bigint           not null, primary key
#  title       :string           not null
#  content     :text
#  user_id     :bigint           not null
#  status      :integer          default("draft"), not null
#  published_at :datetime
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Table name: comments
#
#  id         :bigint           not null, primary key
#  content    :text             not null
#  post_id    :bigint           not null
#  user_id    :bigint           not null
#  approved   :boolean          default(false), not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  enum status: { active: 0, inactive: 1, suspended: 2 }
  
  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :destroy
  
  scope :active, -> { where(status: :active) }
  scope :with_posts, -> { joins(:posts).distinct }
  scope :recent, -> { where(created_at: 30.days.ago..) }
  
  validates :email, presence: true, uniqueness: true
  validates :name, presence: true
end

class Post < ApplicationRecord
  enum status: { draft: 0, published: 1, archived: 2 }
  
  belongs_to :user
  has_many :comments, dependent: :destroy
  
  scope :published, -> { where(status: :published) }
  scope :recent, -> { where(created_at: 7.days.ago..) }
  scope :with_comments, -> { joins(:comments).distinct }
  scope :by_active_users, -> { joins(:user).merge(User.active) }
  
  validates :title, presence: true
  validates :user_id, presence: true
end

class Comment < ApplicationRecord
  belongs_to :post
  belongs_to :user
  
  scope :approved, -> { where(approved: true) }
  scope :pending, -> { where(approved: false) }
  scope :recent, -> { where(created_at: 24.hours.ago..) }
  scope :by_active_users, -> { joins(:user).merge(User.active) }
  scope :on_published_posts, -> { joins(:post).merge(Post.published) }
  
  validates :content, presence: true
end
```

```ruby
class ApplicationController < ActionController::Base
  private
  
  def current_user
    @current_user ||= User.find(session[:user_id]) if session[:user_id]
  end
  
  def require_login
    redirect_to login_path unless current_user
  end
end

class PostsController < ApplicationController
  before_action :require_login
  
  def index
    @posts = current_user.posts.published.includes(:comments)
  end
  
  def show
    @post = Post.find(params[:id])
    @comments = @post.comments.approved.includes(:user)
  end
end
```