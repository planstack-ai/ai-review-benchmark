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
#  role       :integer          default("member"), not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: posts
#
#  id          :bigint           not null, primary key
#  title       :string           not null
#  content     :text
#  status      :integer          default("draft"), not null
#  user_id     :bigint           not null
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
  enum role: { member: 0, moderator: 1, admin: 2 }

  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true

  scope :active, -> { where(status: :active) }
  scope :by_role, ->(role) { where(role: role) }
  scope :recent, -> { order(created_at: :desc) }
end

class Post < ApplicationRecord
  enum status: { draft: 0, published: 1, archived: 2 }

  belongs_to :user
  has_many :comments, dependent: :destroy

  validates :title, presence: true
  validates :user_id, presence: true

  scope :published, -> { where(status: :published) }
  scope :by_author, ->(user) { where(user: user) }
  scope :recent, -> { order(created_at: :desc) }
  scope :with_content, -> { where.not(content: [nil, '']) }
end

class Comment < ApplicationRecord
  belongs_to :post
  belongs_to :user

  validates :content, presence: true

  scope :approved, -> { where(approved: true) }
  scope :pending, -> { where(approved: false) }
  scope :for_post, ->(post) { where(post: post) }
  scope :by_user, ->(user) { where(user: user) }
  scope :recent, -> { order(created_at: :desc) }
end

class ApplicationController < ActionController::Base
  protect_from_forgery with: :exception

  private

  def current_user
    @current_user ||= User.find(session[:user_id]) if session[:user_id]
  end

  def require_login
    redirect_to login_path unless current_user
  end

  def require_admin
    redirect_to root_path unless current_user&.admin?
  end
end

class PostsController < ApplicationController
  before_action :require_login, except: [:index, :show]
  before_action :set_post, only: [:show, :edit, :update, :destroy]

  def index
    @posts = Post.published.includes(:user).recent
  end

  def show
    @comments = @post.comments.approved.includes(:user).recent
  end

  private

  def set_post
    @post = Post.find(params[:id])
  end

  def post_params
    params.require(:post).permit(:title, :content, :status)
  end
end
```