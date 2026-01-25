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
#  id               :bigint           not null, primary key
#  user_id          :bigint           not null
#  title            :string           not null
#  content          :text
#  published_at     :datetime
#  comments_count   :integer          default(0), not null
#  likes_count      :integer          default(0), not null
#  created_at       :datetime         not null
#  updated_at       :datetime         not null
#
# Table name: comments
#
#  id         :bigint           not null, primary key
#  post_id    :bigint           not null
#  user_id    :bigint           not null
#  content    :text             not null
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
```

## Models

```ruby
class User < ApplicationRecord
  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :destroy
  has_many :likes, dependent: :destroy

  validates :email, presence: true, uniqueness: true
  validates :name, presence: true
end

class Post < ApplicationRecord
  belongs_to :user
  has_many :comments, dependent: :destroy
  has_many :likes, dependent: :destroy

  validates :title, presence: true
  validates :user_id, presence: true

  scope :published, -> { where.not(published_at: nil) }
  scope :recent, -> { order(created_at: :desc) }
  scope :popular, -> { order(likes_count: :desc, comments_count: :desc) }

  def published?
    published_at.present?
  end

  def publish!
    update!(published_at: Time.current)
  end
end

class Comment < ApplicationRecord
  belongs_to :post
  belongs_to :user

  validates :content, presence: true

  scope :recent, -> { order(created_at: :desc) }

  after_create :increment_post_counter
  after_destroy :decrement_post_counter

  private

  def increment_post_counter
    post.increment!(:comments_count)
  end

  def decrement_post_counter
    post.decrement!(:comments_count)
  end
end

class Like < ApplicationRecord
  belongs_to :post
  belongs_to :user

  validates :user_id, uniqueness: { scope: :post_id }

  after_create :increment_post_counter
  after_destroy :decrement_post_counter

  private

  def increment_post_counter
    post.increment!(:likes_count)
  end

  def decrement_post_counter
    post.decrement!(:likes_count)
  end
end
```