# Existing Codebase

## Schema

```ruby
# == Schema Information
#
# Table name: repositories
#
#  id         :bigint           not null, primary key
#  name       :string           not null
#  full_name  :string           not null
#  created_at :datetime         not null
#  updated_at :datetime         not null
#
# Table name: pull_requests
#
#  id            :bigint           not null, primary key
#  repository_id :bigint           not null
#  number        :integer          not null
#  title         :string           not null
#  review_status :string           default("pending")
#  reviewed_at   :datetime
#  created_at    :datetime         not null
#  updated_at    :datetime         not null
#
# Table name: code_reviews
#
#  id              :bigint           not null, primary key
#  repository_id   :bigint           not null
#  pull_request_id :bigint           not null
#  reviewer_id     :bigint           not null
#  status          :string           default("pending"), not null
#  automated       :boolean          default(false)
#  started_at      :datetime
#  completed_at    :datetime
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
#
# Table name: review_comments
#
#  id              :bigint           not null, primary key
#  pull_request_id :bigint           not null
#  reviewer_id     :bigint           not null
#  file_path       :string           not null
#  line_number     :integer
#  comment         :text             not null
#  severity        :string
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
#
# Table name: changed_files
#
#  id              :bigint           not null, primary key
#  pull_request_id :bigint           not null
#  path            :string           not null
#  content         :text
#  change_type     :string           not null
#  created_at      :datetime         not null
#  updated_at      :datetime         not null
```

## Models

```ruby
class Repository < ApplicationRecord
  has_many :pull_requests, dependent: :destroy
  has_many :code_reviews, dependent: :destroy

  validates :name, :full_name, presence: true
end

class PullRequest < ApplicationRecord
  belongs_to :repository
  has_many :code_reviews, dependent: :destroy
  has_many :review_comments, dependent: :destroy
  has_many :changed_files, dependent: :destroy

  validates :number, presence: true
  validates :title, presence: true
end

class CodeReview < ApplicationRecord
  belongs_to :repository
  belongs_to :pull_request
  belongs_to :reviewer, class_name: 'User'

  validates :status, inclusion: { in: %w[pending in_progress completed] }
end

class ReviewComment < ApplicationRecord
  belongs_to :pull_request
  belongs_to :reviewer, class_name: 'User'

  validates :file_path, :comment, presence: true
end

class ChangedFile < ApplicationRecord
  belongs_to :pull_request

  validates :path, :change_type, presence: true

  def ruby_file?
    path.end_with?('.rb')
  end

  def javascript_file?
    path.end_with?('.js', '.jsx', '.ts', '.tsx')
  end

  def test_file?
    path.include?('spec/') || path.include?('test/')
  end

  def name
    File.basename(path)
  end
end
```

## Jobs

```ruby
class NotifyReviewCompleteJob < ApplicationJob
  queue_as :notifications

  def perform(review_id)
    review = CodeReview.find(review_id)
    # Send notification logic
  end
end

class UpdateMetricsJob < ApplicationJob
  queue_as :metrics

  def perform(repository_id)
    # Update metrics logic
  end
end

class NotifyDeveloperJob < ApplicationJob
  queue_as :notifications

  def perform(pull_request_id, errors_count)
    # Notify developer logic
  end
end
```

## Analyzers (External Services)

```ruby
class RubocopAnalyzer
  def initialize(content); end
  def analyze; []; end
end

class SecurityScanner
  def initialize(content); end
  def scan; []; end
end

class EslintAnalyzer
  def initialize(content); end
  def analyze; []; end
end

class TestCoverageAnalyzer
  def initialize(file); end
  def calculate_coverage; 85; end
end
```
