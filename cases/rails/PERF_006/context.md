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
#  role       :string           default("user")
#  updated_at :datetime         not null
#  created_at :datetime         not null
#
# Table name: posts
#
#  id          :bigint           not null, primary key
#  title       :string           not null
#  content     :text
#  user_id     :bigint           not null
#  published   :boolean          default(false)
#  updated_at  :datetime         not null
#  created_at  :datetime         not null
#
# Table name: comments
#
#  id         :bigint           not null, primary key
#  content    :text             not null
#  user_id    :bigint           not null
#  post_id    :bigint           not null
#  updated_at :datetime         not null
#  created_at :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :destroy
  
  validates :email, presence: true, uniqueness: true
  validates :name, presence: true
  
  enum role: { user: 'user', admin: 'admin', moderator: 'moderator' }
  
  scope :active, -> { where('updated_at > ?', 30.days.ago) }
  
  def display_name
    name.presence || email.split('@').first
  end
  
  def admin_or_moderator?
    admin? || moderator?
  end
end

class Post < ApplicationRecord
  belongs_to :user
  has_many :comments, dependent: :destroy
  
  validates :title, presence: true
  validates :content, presence: true
  
  scope :published, -> { where(published: true) }
  scope :recent, -> { order(created_at: :desc) }
  scope :by_user, ->(user) { where(user: user) }
  
  def excerpt(limit = 100)
    content.truncate(limit)
  end
  
  def comment_count
    comments.count
  end
end

class Comment < ApplicationRecord
  belongs_to :user
  belongs_to :post
  
  validates :content, presence: true
  
  scope :recent, -> { order(created_at: :desc) }
  scope :by_user, ->(user) { where(user: user) }
  
  def author_name
    user.display_name
  end
end

class ApplicationController < ActionController::Base
  before_action :authenticate_user!
  
  private
  
  def current_user
    @current_user ||= User.find(session[:user_id]) if session[:user_id]
  end
  
  def authenticate_user!
    redirect_to login_path unless current_user
  end
end
```

## Usage Guidelines

- Never load entire tables into memory. Use `find_each` or `find_in_batches` for batch processing large datasets.

- Design cache keys carefully. Include all variables that affect the cached content (user_id, locale, etc.) to prevent showing wrong data.

