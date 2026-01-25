# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: users
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  email      :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: posts
#
#  id         :bigint           not null, primary key
#  title      :string           not null
#  content    :text
#  user_id    :bigint           not null
#  published  :boolean          default(false)
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
# Table name: tags
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: post_tags
#
#  id      :bigint  not null, primary key
#  post_id :bigint  not null
#  tag_id  :bigint  not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :destroy
  has_many :published_posts, -> { where(published: true) }, class_name: 'Post'

  validates :name, :email, presence: true
  validates :email, uniqueness: true

  scope :active, -> { where('created_at > ?', 1.year.ago) }
end

class Post < ApplicationRecord
  belongs_to :user
  has_many :comments, dependent: :destroy
  has_many :post_tags, dependent: :destroy
  has_many :tags, through: :post_tags
  has_many :commenters, -> { distinct }, through: :comments, source: :user

  validates :title, presence: true

  scope :published, -> { where(published: true) }
  scope :recent, -> { order(created_at: :desc) }
  scope :with_comments, -> { joins(:comments).distinct }

  def comment_count
    comments.count
  end

  def tag_names
    tags.pluck(:name)
  end
end

class Comment < ApplicationRecord
  belongs_to :post
  belongs_to :user

  validates :content, presence: true

  scope :recent, -> { order(created_at: :desc) }
end

class Tag < ApplicationRecord
  has_many :post_tags, dependent: :destroy
  has_many :posts, through: :post_tags

  validates :name, presence: true, uniqueness: true

  scope :popular, -> { joins(:posts).group('tags.id').having('COUNT(posts.id) > 5') }
end

class PostTag < ApplicationRecord
  belongs_to :post
  belongs_to :tag
end
```
