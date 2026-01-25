# Existing Codebase

## Data Scale Notes

Projects typically have 10-100 tasks, 5-20 team members, and 50-500 comments.

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
# Table name: projects
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  user_id    :bigint           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: tasks
#
#  id          :bigint           not null, primary key
#  title       :string           not null
#  completed   :boolean          default(false)
#  project_id  :bigint           not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Table name: team_members
#
#  id         :bigint           not null, primary key
#  full_name  :string           not null
#  active     :boolean          default(true)
#  project_id :bigint           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: comments
#
#  id         :bigint           not null, primary key
#  content    :text             not null
#  project_id :bigint           not null
#  author_id  :bigint           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  has_many :projects, dependent: :destroy

  validates :name, :email, presence: true
  validates :email, uniqueness: true
end

class Project < ApplicationRecord
  belongs_to :user
  has_many :tasks, dependent: :destroy
  has_many :team_members, dependent: :destroy
  has_many :comments, dependent: :destroy

  validates :name, presence: true

  scope :active, -> { where('created_at > ?', 30.days.ago) }
end

class Task < ApplicationRecord
  belongs_to :project

  validates :title, presence: true

  scope :completed, -> { where(completed: true) }
  scope :pending, -> { where(completed: false) }

  def completed?
    completed
  end
end

class TeamMember < ApplicationRecord
  belongs_to :project
  has_many :comments, foreign_key: :author_id, dependent: :nullify

  validates :full_name, presence: true

  scope :active, -> { where(active: true) }

  def active?
    active
  end
end

class Comment < ApplicationRecord
  belongs_to :project
  belongs_to :author, class_name: 'TeamMember'

  validates :content, presence: true

  scope :recent, -> { order(created_at: :desc) }
end
```
