# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: projects
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  status     :string           default("active"), not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: review_sessions
#
#  id                  :bigint           not null, primary key
#  project_id          :bigint           not null
#  started_at          :datetime
#  completed_at        :datetime
#  status              :string           default("pending"), not null
#  benchmark_type      :string
#  accuracy_percentage :decimal(5, 2)
#  precision_score     :decimal(5, 3)
#  recall_score        :decimal(5, 3)
#  created_at          :datetime         not null
#  updated_at          :datetime         not null
#
# Table name: benchmark_files
#
#  id                :bigint           not null, primary key
#  review_session_id :bigint           not null
#  file_path         :string           not null
#  content           :text
#  expected_issues   :integer          default(0)
#  temporary         :boolean          default(false)
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#
# Table name: test_cases
#
#  id                :bigint           not null, primary key
#  review_session_id :bigint           not null
#  pattern_name      :string           not null
#  severity          :string
#  expected_result   :boolean          default(true)
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
#
# Table name: code_issues
#
#  id                :bigint           not null, primary key
#  review_session_id :bigint           not null
#  file_path         :string           not null
#  line_number       :integer
#  issue_type        :string           not null
#  description       :text
#  severity          :string
#  created_at        :datetime         not null
#  updated_at        :datetime         not null
```

## Models

```ruby
class Project < ApplicationRecord
  has_many :review_sessions, dependent: :destroy

  validates :name, presence: true
  validates :status, inclusion: { in: %w[active inactive archived] }

  scope :active, -> { where(status: 'active') }

  def active?
    status == 'active'
  end
end

class ReviewSession < ApplicationRecord
  belongs_to :project
  has_many :benchmark_files, dependent: :destroy
  has_many :test_cases, dependent: :destroy
  has_many :code_issues, dependent: :destroy

  validates :project_id, presence: true
  validates :status, inclusion: { in: %w[pending running completed failed] }
end

class BenchmarkFile < ApplicationRecord
  belongs_to :review_session

  validates :file_path, presence: true
end

class TestCase < ApplicationRecord
  belongs_to :review_session

  validates :pattern_name, presence: true
end

class CodeIssue < ApplicationRecord
  belongs_to :review_session

  validates :file_path, presence: true
  validates :issue_type, presence: true
end
```
