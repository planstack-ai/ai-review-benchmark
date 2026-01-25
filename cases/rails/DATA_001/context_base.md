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
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_users_on_email  (email) UNIQUE
#

# Table name: posts
#
#  id         :bigint           not null, primary key
#  title      :string           not null
#  content    :text
#  user_id    :bigint           not null
#  status     :string           default("draft")
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_posts_on_user_id  (user_id)
#  index_posts_on_status   (status)
#

# Table name: comments
#
#  id         :bigint           not null, primary key
#  content    :text             not null
#  post_id    :bigint           not null
#  user_id    :bigint           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Indexes
#
#  index_comments_on_post_id  (post_id)
#  index_comments_on_user_id  (user_id)
#
```

## Models

```ruby
class User < ApplicationRecord
  validates :email, presence: true, uniqueness: true
  validates :name, presence: true

  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :destroy

  scope :active, -> { joins(:posts).where(posts: { status: 'published' }).distinct }
  
  def full_name
    name.titleize
  end
end

class Post < ApplicationRecord
  VALID_STATUSES = %w[draft published archived].freeze
  
  validates :title, presence: true
  validates :user_id, presence: true
  validates :status, inclusion: { in: VALID_STATUSES }
  
  belongs_to :user
  has_many :comments, dependent: :destroy
  
  scope :published, -> { where(status: 'published') }
  scope :by_user, ->(user) { where(user: user) }
  scope :recent, -> { order(created_at: :desc) }
  
  before_validation :set_default_status
  
  def published?
    status == 'published'
  end
  
  def comment_count
    comments.count
  end
  
  private
  
  def set_default_status
    self.status ||= 'draft'
  end
end

class Comment < ApplicationRecord
  validates :content, presence: true
  validates :post_id, presence: true
  validates :user_id, presence: true
  
  belongs_to :post
  belongs_to :user
  
  scope :recent, -> { order(created_at: :desc) }
  scope :for_post, ->(post) { where(post: post) }
  scope :by_user, ->(user) { where(user: user) }
  
  def author_name
    user&.name || 'Anonymous'
  end
end

class ApplicationRecord < ActiveRecord::Base
  primary_abstract_class
  
  def self.exists_and_belongs_to?(id, parent_association, parent_id)
    return false if id.blank? || parent_id.blank?
    
    where(id: id, "#{parent_association}_id": parent_id).exists?
  end
end
```
