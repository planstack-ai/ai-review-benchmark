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
#  id               :bigint           not null, primary key
#  title            :string           not null
#  content          :text
#  user_id          :bigint           not null
#  published        :boolean          default(false)
#  comments_count   :integer          default(0)
#  created_at       :datetime         not null
#  updated_at       :datetime         not null
#
# Table name: comments
#
#  id         :bigint           not null, primary key
#  content    :text             not null
#  post_id    :bigint           not null
#  user_id    :bigint           not null
#  approved   :boolean          default(false)
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :posts, dependent: :destroy
  has_many :comments, dependent: :destroy

  validates :name, presence: true
  validates :email, presence: true, uniqueness: true

  scope :active, -> { joins(:posts).where(posts: { published: true }).distinct }
end

class Post < ApplicationRecord
  belongs_to :user
  has_many :comments, dependent: :destroy

  validates :title, presence: true
  validates :user_id, presence: true

  scope :published, -> { where(published: true) }
  scope :with_comments, -> { where('comments_count > 0') }
  scope :recent, -> { order(created_at: :desc) }

  def publish!
    update!(published: true)
  end

  def approved_comments
    comments.where(approved: true)
  end

  def pending_comments
    comments.where(approved: false)
  end
end

class Comment < ApplicationRecord
  belongs_to :post
  belongs_to :user

  validates :content, presence: true
  validates :post_id, presence: true
  validates :user_id, presence: true

  scope :approved, -> { where(approved: true) }
  scope :pending, -> { where(approved: false) }
  scope :recent, -> { order(created_at: :desc) }

  def approve!
    update!(approved: true)
  end

  def reject!
    destroy
  end
end
```