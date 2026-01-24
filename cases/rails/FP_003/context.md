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
#  role       :string           default("member")
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: projects
#
#  id          :bigint           not null, primary key
#  title       :string           not null
#  description :text
#  status      :string           default("active")
#  user_id     :bigint           not null
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Table name: tasks
#
#  id          :bigint           not null, primary key
#  title       :string           not null
#  description :text
#  status      :string           default("pending")
#  priority    :string           default("medium")
#  project_id  :bigint           not null
#  assignee_id :bigint
#  created_at  :datetime         not null
#  updated_at  :datetime         not null
#
# Table name: comments
#
#  id         :bigint           not null, primary key
#  content    :text             not null
#  task_id    :bigint           not null
#  author_id  :bigint           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
```

## Models

```ruby
class User < ApplicationRecord
  ROLES = %w[admin manager member].freeze
  
  validates :email, presence: true, uniqueness: true
  validates :name, presence: true
  validates :role, inclusion: { in: ROLES }
  
  scope :active, -> { where.not(role: nil) }
  scope :managers, -> { where(role: 'manager') }
  scope :admins, -> { where(role: 'admin') }
  
  def admin?
    role == 'admin'
  end
  
  def manager?
    role == 'manager'
  end
end

class Project < ApplicationRecord
  STATUSES = %w[active archived completed].freeze
  
  validates :title, presence: true
  validates :status, inclusion: { in: STATUSES }
  validates :user_id, presence: true
  
  scope :active, -> { where(status: 'active') }
  scope :completed, -> { where(status: 'completed') }
  scope :recent, -> { order(created_at: :desc) }
  
  def active?
    status == 'active'
  end
  
  def completed?
    status == 'completed'
  end
end

class Task < ApplicationRecord
  STATUSES = %w[pending in_progress completed].freeze
  PRIORITIES = %w[low medium high urgent].freeze
  
  validates :title, presence: true
  validates :status, inclusion: { in: STATUSES }
  validates :priority, inclusion: { in: PRIORITIES }
  validates :project_id, presence: true
  
  scope :pending, -> { where(status: 'pending') }
  scope :completed, -> { where(status: 'completed') }
  scope :high_priority, -> { where(priority: ['high', 'urgent']) }
  scope :assigned, -> { where.not(assignee_id: nil) }
  scope :unassigned, -> { where(assignee_id: nil) }
  
  def completed?
    status == 'completed'
  end
  
  def assigned?
    assignee_id.present?
  end
end

class Comment < ApplicationRecord
  validates :content, presence: true
  validates :task_id, presence: true
  validates :author_id, presence: true
  
  scope :recent, -> { order(created_at: :desc) }
  scope :by_author, ->(author) { where(author_id: author.id) }
end
```