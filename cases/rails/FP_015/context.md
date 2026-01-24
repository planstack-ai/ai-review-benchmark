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
#  id      :bigint           not null, primary key
#  post_id :bigint           not null
#  tag_id  :bigint           not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :destroy

  validates :name, :email, presence: true
  validates :email, uniqueness: true

  scope :active, -> { where('created_at > ?', 30.days.ago) }
end

class Post < ApplicationRecord
  belongs_to :user
  has_many :comments, dependent: :destroy
  has_many :post_tags, dependent: :destroy
  has_many :tags, through: :post_tags

  validates :title, presence: true

  scope :published, -> { where.not(content: nil) }
  scope :recent, -> { order(created_at: :desc) }
  scope :with_associations, -> { includes(:user, :comments, :tags) }

  def comment_count
    comments.count
  end

  def author_name
    user.name
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

  def author_name
    user.name
  end

  def post_title
    post.title
  end
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