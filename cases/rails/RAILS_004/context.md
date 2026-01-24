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
# Table name: posts
#
#  id         :bigint           not null, primary key
#  title      :string           not null
#  content    :text
#  user_id    :bigint           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
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
# Table name: likes
#
#  id         :bigint           not null, primary key
#  post_id    :bigint           not null
#  user_id    :bigint           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: tags
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: post_tags
#
#  id         :bigint           not null, primary key
#  post_id    :bigint           not null
#  tag_id     :bigint           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  validates :email, presence: true, uniqueness: true
  validates :name, presence: true

  has_many :posts
  has_many :comments
  has_many :likes

  scope :active, -> { where(deleted_at: nil) }
  
  def full_profile_complete?
    email.present? && name.present?
  end
end

class Post < ApplicationRecord
  validates :title, presence: true
  validates :user_id, presence: true

  belongs_to :user
  has_many :comments
  has_many :likes
  has_many :post_tags
  has_many :tags, through: :post_tags

  scope :published, -> { where.not(published_at: nil) }
  scope :recent, -> { order(created_at: :desc) }

  def published?
    published_at.present?
  end

  def like_count
    likes.count
  end
end

class Comment < ApplicationRecord
  validates :content, presence: true
  validates :post_id, presence: true
  validates :user_id, presence: true

  belongs_to :post
  belongs_to :user

  scope :recent, -> { order(created_at: :desc) }
  scope :approved, -> { where(approved: true) }

  def excerpt(limit = 100)
    content.truncate(limit)
  end
end

class Like < ApplicationRecord
  validates :post_id, presence: true
  validates :user_id, presence: true
  validates :user_id, uniqueness: { scope: :post_id }

  belongs_to :post
  belongs_to :user

  scope :recent, -> { order(created_at: :desc) }
end

class Tag < ApplicationRecord
  validates :name, presence: true, uniqueness: true

  has_many :post_tags
  has_many :posts, through: :post_tags

  scope :popular, -> { joins(:posts).group('tags.id').having('COUNT(posts.id) > 5') }

  def slug
    name.parameterize
  end
end

class PostTag < ApplicationRecord
  validates :post_id, presence: true
  validates :tag_id, presence: true
  validates :post_id, uniqueness: { scope: :tag_id }

  belongs_to :post
  belongs_to :tag
end
```